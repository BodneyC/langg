from ..util import namespace_ext as ns_ext
from ..lib.ttop import TreeTop
from ..translate.translator import Translator

import json
from types import SimpleNamespace


# Todo: Shouldn't be printing if this is going to be an API...
def treegen(ttop: TreeTop, args: SimpleNamespace) -> None:
    op_data: SimpleNamespace = args.op_data

    if op_data.json_out:
        print(ttop.to_json())

    if op_data.json_outfile:
        ttop.write_json(op_data.json_outfile)

    if op_data.dot_out:
        print(ttop.to_dot())

    if op_data.dot_outfile:
        ttop.write_dot(op_data.dot_outfile)

    if op_data.proto_outfile:
        ttop.write_protobuf(op_data.proto_outfile)

    if op_data.stats:
        print(json.dumps(ttop.longest_branches(), indent=2))
        print(json.dumps(ttop.statistics(), indent=2))


def translate(ttop: TreeTop, args: SimpleNamespace) -> None:
    translator: Translator = Translator(ttop, args)

    if args.op_data.stdin:
        translator.translate_stdin()
    else:
        txt: str = translator.translate_text()
        print(txt)


def run(args_dict: dict) -> None:
    args: SimpleNamespace = ns_ext.wrap_namespace(args_dict)

    if args.infiles:
        ttop = TreeTop.from_cli(args)
        ttop.parse_infiles()
        ttop.sort_trees()
    elif args.proto_in:
        ttop = TreeTop.from_protobuf(args.proto_in)
    elif args.json_in:
        ttop = TreeTop.from_json(args.json_in)
    else:
        raise Exception('Unknown input format')

    if args.cmd in ('generate', 'gen', 'treegen'):
        treegen(ttop, args)
    elif args.cmd in ('translate', 'trn', 'langg'):
        translate(ttop, args)
    else:
        raise Exception(f'Unknown subcommand: {args.cmd}')
