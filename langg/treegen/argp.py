import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    # Input

    input_group = parser.add_mutually_exclusive_group()

    input_group.add_argument('-i', '--infiles', '--input-files', nargs='+',
                             type=str, help='Input dictionary files')

    input_group.add_argument('--proto-in', '--protobuf-infile', type=str,
                             help='Read tree data from protobuf file')

    # Output

    parser.add_argument('--json', action='store_true',
                        help='Print JSON to stdout')

    parser.add_argument('--json-outfile', type=str,
                        help='Print JSON to given filename')

    parser.add_argument('--dot', action='store_true',
                        help='Print dotviz to stdout')

    parser.add_argument('--dot-outfile', type=str,
                        help='Print dotviz to given filename')

    parser.add_argument('--proto-out', '--protobuf-outfile', type=str,
                        help='Print protobuf bin to given filename')

    # Behaviour

    parser.add_argument('--separate-trees', action='store_true',
                        help='Generate separate tree per dictionary file')

    parser.add_argument('--chars', '--considered-chars', type=str,
                        help='Chars to consider in the dictionary files')

    parser.add_argument('--root-chars', type=str,
                        help='Only process words starting with these chars')

    parser.add_argument('--full', '--full-words', action='store_true',
                        help='Only add full words to the tree(s)')

    parser.add_argument('--log', '--log-level', type=str,
                        help='Set the log level', default='NOTSET')

    # Reporting

    parser.add_argument('-k', '--kmers', type=int, default=3,
                        help='Reports shound be made on k length substrings')

    parser.add_argument('-s', '--stats', '--statistics', action='store_true',
                        help='Print some tree stats to stdout')

    return parser.parse_args()


if __name__ == '__main__':
    print(parse_args())
