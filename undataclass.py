import ast
import dataclasses
from textwrap import dedent, indent


__all__ = ["undataclass"]


def is_dataclass_decorator(node):
    match node:
        case ast.Call(func=ast.Attribute(
            value=ast.Name(id="dataclasses"),
            attr="dataclass"),
        ):
            return True
        case ast.Call(func=ast.Name(id="dataclass")):
            return True
        case ast.Attribute(
            value=ast.Name(id="dataclasses"),
            attr="dataclass"
        ):
            return True
        case ast.Name(id="dataclass"):
            return True
        case _:
            return False


def parse_decorator_options(node):
    match node:
        case ast.Call():
            return {
                subnode.arg: ast.literal_eval(subnode.value)
                for subnode in node.keywords
            }
        case ast.Attribute() | ast.Name():
            return {}
        case _:
            assert False  # There's a bug!


def attr_tuple(object_name, fields):
    joined_names = ", ".join([
        f"{object_name}.{f.name}"
        for f in fields
    ])
    if len(fields) == 1:
        return f"({joined_names},)"
    else:
        return f"({joined_names})"


def attr_name_tuple(fields):
    joined_names = ", ".join([
        repr(f.name)
        for f in fields
    ])
    if len(fields) == 1:
        return f"({joined_names},)"
    else:
        return f"({joined_names})"


def make_slots(fields):
    return f"__slots__ = {attr_name_tuple(fields)}"


def make_match_args(fields):
    fields = [f for f in fields if f.init]
    return f"__match_args__ = {attr_name_tuple(fields)}"


def make_arg(field):
    if field.default is not dataclasses.MISSING:
        return f"{field.name}: {field.type} = {field.default}"
    elif field.default_factory is not dataclasses.MISSING:
        return f"{field.name}: {field.type} = None"
    else:
        return f"{field.name}: {field.type}"


def make_init(fields, post_init_nodes, init_vars, frozen, kw_only_fields):
    fields = [f for f in fields if f.init]
    arg_list = [
        make_arg(f)
        for f in fields
        if f not in kw_only_fields
    ]
    if kw_only_fields:
        arg_list.append("*")
        arg_list += [
            make_arg(f)
            for f in fields
            if f in kw_only_fields
        ]
    init_args = ", ".join(arg_list)
    if frozen:
        init_body = "\n".join([
            f"object.__setattr__(self, {f.name!r}, {f.name})"
            for f in fields
        ])
    else:
        init_body = "\n".join([
            f"self.{f.name} = {f.name}"
            for f in fields
        ])
    if any(f.default_factory is not dataclasses.MISSING for f in fields):
        init_body = "".join([
            f"if {f.name} is None:\n    {f.name} = {f.default_factory}()\n"
            for f in fields
            if f.default_factory is not dataclasses.MISSING
        ]) + init_body
    return dedent("""
        def __init__(self, {init_args}) -> None:
        {init_body}
        {post_init}
    """).format(
        init_args=init_args,
        init_body=indent(init_body, " "*4),
        post_init=indent(ast.unparse(post_init_nodes), " "*4),
    )


def make_repr(fields):
    repr_args = ", ".join([
        f"{f.name}={{self.{f.name}!r}}"
        for f in fields
        if f.repr
    ])
    return dedent("""
        def __repr__(self):
            cls = type(self).__name__
            return f"{{cls}}({repr_args})"
    """).format(repr_args=repr_args)


def make_order(operator, class_name, fields):
    names = {"==": "eq", "<": "lt"}
    fields = [f for f in fields if f.compare]
    self_tuple = attr_tuple("self", fields)
    other_tuple = attr_tuple("other", fields)
    return dedent(f"""
        def __{names[operator]}__(self, other):
            if not isinstance(other, {class_name}):
                return NotImplemented
            return {self_tuple} {operator} {other_tuple}
    """)


def make_hash(fields):
    self_tuple = attr_tuple("self", [
        f
        for f in fields
        if f.compare
    ])
    return dedent(f"""
        def __hash__(self):
            return hash({self_tuple})
    """)


def make_setattr_and_delattr():
    return dedent("""
        def __setattr__(self, name, value):
            raise AttributeError(f"Can't set attribute {name!r}")
        def __delattr__(self, name):
            raise AttributeError(f"Can't delete attribute {name!r}")
    """)


def make_setstate_and_getstate(fields):
    return dedent(f"""
        def __getstate__(self):
            return {attr_tuple("self", fields)}
        def __setstate__(self, state):
            fields = {attr_name_tuple(fields)}
            for field, value in zip(fields, state):
                object.__setattr__(self, field, value)
    """)


def process_kw_only_fields(options, fields):
    if _ := next((f for f in fields if f.type.endswith("KW_ONLY")), None):
        kw_only_fields = fields[fields.index(_)+1:]
        fields.remove(_)
    else:
        kw_only_fields = []
    if any(f.kw_only for f in fields):
        old_kw_only_fields = list(kw_only_fields)
        kw_only_fields = [
            f
            for f in fields
            if f.kw_only is True or f in old_kw_only_fields
        ]
    if options.get("kw_only"):
        kw_only_fields = fields
    return kw_only_fields


def process_init_vars(fields):
    init_var_fields = [
        f
        for f in fields
        if "InitVar" in f.type
    ]
    init_fields = list(fields)
    for field in init_var_fields:
        fields.remove(field)
    return init_fields, [f.name for f in init_var_fields]


def make_dataclass_methods(class_name, options, fields, post_init):
    nodes = []
    kw_only_fields = process_kw_only_fields(options, fields)
    init_fields, init_vars = process_init_vars(fields)
    if options.get("slots", False):
        nodes += ast.parse(make_slots(fields)).body
    if options.get("match_args", True):
        nodes += ast.parse(make_match_args(fields)).body
    if options.get("init", True):
        nodes += ast.parse(make_init(
            init_fields,
            post_init,
            init_vars,
            options.get("frozen", False),
            kw_only_fields,
        )).body
    if options.get("repr", True):
        nodes += ast.parse(make_repr(fields)).body
    if options.get("compare", True):
        nodes += ast.parse(make_order("==", class_name, fields)).body
    if options.get("order", True):
        nodes += ast.parse(make_order("<", class_name, fields)).body
    if (options.get("frozen", False) and options.get("eq", True)
            or options.get("unsafe_hash", False)):
        nodes += ast.parse(make_hash(fields)).body
    if options.get("frozen", False):
        nodes += ast.parse(make_setattr_and_delattr()).body
        if options.get("slots", False):
            nodes += ast.parse(make_setstate_and_getstate(fields)).body
    return nodes


def parse_field_argument(name, value_node):
    if name not in ("default", "default_factory", "metadata"):
        return ast.literal_eval(value_node)
    return ast.unparse(value_node)


def make_field(subnode, **kwargs):
    match subnode:
        case ast.AnnAssign(value=None):
            field = dataclasses.field()
        case ast.AnnAssign(value=ast.Call(
            func=ast.Name(id="field")
                |
                ast.Attribute(value=ast.Name(id="dataclasses"), attr="field")
        )):
            field = dataclasses.field(**{
                kwarg.arg: parse_field_argument(kwarg.arg, kwarg.value)
                for kwarg in subnode.value.keywords
            })
        case ast.AnnAssign():
            field = dataclasses.field(default=ast.unparse(subnode.value))
    field.name = subnode.target.id
    field.type = ast.unparse(subnode.annotation)
    return field


def update_dataclass_node(node):
    order = False
    DATACLASS_STUFF_HERE = object()
    fields = []
    new_body = []
    post_init = []
    for subnode in node.body:
        match subnode:
            case ast.AnnAssign() if (
                "ClassVar" not in ast.unparse(subnode.annotation)
            ):
                fields.append(make_field(subnode))
            case ast.FunctionDef():
                if DATACLASS_STUFF_HERE not in new_body:
                    new_body.append(DATACLASS_STUFF_HERE)
                if subnode.name == "__post_init__":
                    post_init = subnode.body
                else:
                    new_body.append(subnode)
            case _:
                new_body.append(subnode)
    new_decorator_list = []
    options = {}
    for subnode in node.decorator_list:
        if is_dataclass_decorator(subnode):
            options = parse_decorator_options(subnode)
        else:
            new_decorator_list.append(subnode)
    if options.get("order"):
        order = True
        new_decorator_list.append(ast.Name(id="total_ordering"))
    node.decorator_list = new_decorator_list
    dataclass_extras = make_dataclass_methods(
        node.name,
        options,
        fields,
        post_init,
    )
    if DATACLASS_STUFF_HERE in new_body:
        index = new_body.index(DATACLASS_STUFF_HERE)
        new_body[index:index+1] = dataclass_extras
    else:
        new_body.extend(dataclass_extras)
    node.body = new_body
    return order


def undataclass(code):
    nodes = ast.parse(code).body
    new_nodes = []
    need_total_ordering = False
    for node in nodes:
        match node:
            case ast.ImportFrom(module="dataclasses"):
                continue  # Don't import dataclasses anymore
            case ast.Import() if node.names[0].name == "dataclasses":
                continue  # Don't import dataclasses anymore
            case ast.ClassDef() if any(
                is_dataclass_decorator(n)
                for n in node.decorator_list
            ):
                need_total_ordering |= update_dataclass_node(node)
                new_nodes.append(node)
            case _:
                new_nodes.append(node)
    if need_total_ordering:
        for i, node in enumerate(new_nodes):
            match node:
                case ast.Expr(value=ast.Constant()):
                    continue
                case ast.Import() | ast.ImportFrom():
                    continue
                case _:
                    break
        new_nodes.insert(
            i,
            *ast.parse("from functools import total_ordering").body,
        )
    return ast.unparse(new_nodes)


def main():
    from argparse import ArgumentParser, FileType
    parser = ArgumentParser()
    parser.add_argument("code_file", type=FileType("rt"))
    args = parser.parse_args()
    print(undataclass(args.code_file.read()))


if __name__ == "__main__":
    main()
