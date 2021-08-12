#!/usr/bin/env python3

from langg.treegen.ttop import TreeTop

import os
import json
import argparse
import logging as log


def treegen(args: argparse.Namespace) -> None:
    # Construction

    if args.infiles:
        tree_top = TreeTop.from_cli(args)
        tree_top.parse_infiles()
        tree_top.sort_trees()
    else:  # if args.proto_in
        tree_top = TreeTop.from_protobuf(args.proto_in)

    # Output

    if args.json:
        print(tree_top.to_json())

    if args.json_outfile:
        tree_top.write_json(args.json_outfile)

    if args.dot:
        print(tree_top.to_dot())

    if args.dot_outfile:
        tree_top.write_dot(args.dot_outfile)

    if args.proto_out:
        tree_top.write_protobuf(args.proto_out)

    if args.stats:
        # print(json.dumps(tree_top.longest_branches(), indent=2))
        print(json.dumps(tree_top.statistics(), indent=2))


if __name__ == '__main__':
    from langg.treegen import argp
    args = argp.parse_args()
    log.basicConfig(level=(os.getenv('LOG_LEVEL') or args.log).upper())
    treegen(args)
