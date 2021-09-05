#!/usr/bin/env python3

from .argp_ext import (
    AliasedSubParsersAction, SeparateNamespaceArgumentParser
)


def parser():
    parser = SeparateNamespaceArgumentParser(
        prog='langg', description='Create your language')

    # Input

    parser.add_argument('-l', '--log', '--log-level', type=str,
                        help='Set the log level', default='DEBUG')

    input_group = parser.add_mutually_exclusive_group()

    input_group.add_argument('-i', '--infile', '--input-file', type=str,
                             dest='infiles', action='append',
                             help='Input dictionary files')

    input_group.add_argument('--proto-in', '--protobuf-infile', type=str,
                             help='Read tree data from protobuf file')

    input_group.add_argument('--json-in', '--json-infile', type=str,
                             help='Read tree data from JSON file')

    # Subcommand setup

    parser.register('action', 'parsers', AliasedSubParsersAction)

    subparsers = parser.add_subparsers(title='commands', metavar='COMMAND',
                                       dest='cmd')

    # -------------------------------------------------------------------------
    # Generate
    # -------------------------------------------------------------------------

    p_gen = subparsers.add_parser('generate', aliases=('gen', 'treegen'),
                                  help='Generate trees from input')

    # Output

    p_gen.add_argument('--json-out', action='store_true',
                       help='Print JSON to stdout')

    p_gen.add_argument('--json-outfile', type=str,
                       help='Print JSON to given filename')

    p_gen.add_argument('--dot-out', action='store_true',
                       help='Print dotviz to stdout')

    p_gen.add_argument('--dot-outfile', type=str,
                       help='Print dotviz to given filename')

    p_gen.add_argument('--proto-outfile', '--protobuf-outfile', type=str,
                       help='Print protobuf bin to given filename')

    # Behaviour

    p_gen.add_argument('--separate-trees', action='store_true',
                       help='Generate separate tree per dictionary file')

    p_gen.add_argument('--chars', '--considered-chars', type=str,
                       help='Chars to consider in the dictionary files')

    p_gen.add_argument('--root-chars', type=str,
                       help='Only process words starting with these chars')

    p_gen.add_argument('--full', '--full-words', action='store_true',
                       help='Only add full words to the tree(s)')

    # Reporting

    p_gen.add_argument('-k', '--kmers', type=int, default=3,
                       help='Reports shound be made on k length substrings')

    p_gen.add_argument('-s', '--stats', '--statistics', action='store_true',
                       help='Print some tree stats to stdout')

    # -------------------------------------------------------------------------
    # Translate
    # -------------------------------------------------------------------------

    p_trn = subparsers.add_parser('translate', aliases=('trn', 'langg'),
                                  help='Use input to generate langg')

    # Input

    p_g_input = p_trn.add_mutually_exclusive_group(required=True)

    p_g_input.add_argument('--stdin', action='store_true',
                           help='Read phrases to translate from stdin')

    p_g_input.add_argument('--txt', '--text', type=str,
                           help='String to translate')

    p_g_input.add_argument('--txt-in', '--txt-infile', type=str,
                           action='append', metavar='txt_infiles',
                           help='File to read and translate')

    # Behaviour

    p_trn.add_argument('-t', '--tree', type=int, default=0,
                       help='Which tree in the input data to use')

    p_trn.add_argument('--seed', type=int,
                       help='Seed to use in random number generation')

    # Output

    p_trn.add_argument('--stdout', action='store_true',
                       help='Write translated phrases to stdout')

    p_trn.add_argument('--txt-outfile', type=str,
                       help='Print JSON to given filename')

    p_bot = subparsers.add_parser('bot', help='Launch the Discord bot')

    p_bot.add_argument('--token', type=str, default=None,
                       help='Supply the discord bot token')

    p_bot.add_argument('--storage-dir', type=str, default=None,
                       help='Where to store uploaded dictionary files')

    return parser


if __name__ == '__main__':
    print(parser()())
