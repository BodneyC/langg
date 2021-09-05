# Langg

Langg is a program written to generate a pseudo-language - really it's just English but with each word swapped out for another and there are a few rules to split/join certain words/word combinations.

## CLI Options

There are three subcommands of use, both `translate` and `generate` require an input file so I have separated out this part of the input below.

### Input

There are three input filetypes, either:

1. Text dictionary input with `--infile`
2. A JSON input describing a set of trees with `--json-in`
3. A [Protobuf](https://developers.google.com/protocol-buffers) file generated previously by the program with `--proto-in`

The [Argparse](https://docs.python.org/3/library/argparse.html) help for the root level is as follows:

```txt
usage: langg [-h] [-l LOG]
             [-i INFILES | --proto-in PROTO_IN | --json-in JSON_IN]
             COMMAND ...

optional arguments:
  -h, --help            show this help message and exit
  -l LOG, --log LOG, --log-level LOG
                        Set the log level
  -i INFILES, --infile INFILES, --input-file INFILES
                        Input dictionary files
  --proto-in PROTO_IN, --protobuf-infile PROTO_IN
                        Read tree data from protobuf file
  --json-in JSON_IN, --json-infile JSON_IN
                        Read tree data from JSON file
```

### Subcommands

#### Generate

This subcommand is used to generate a tree from a given input file (see [Input](#input)).

Several output formats are available to save the tree for later use, usually with the [`translate`](#translate) subcommand. I would advise a Protobuf object for size and speed (compared to JSON particularly).

- `--json-out`: As JSON to stdout
- `--json-outfile`: As JSON to a particular file
- `--dot-out`: As a Dotviz file to stdout
- `--dot-outfile`: As a Dotviz file to a particular file
- `--proto-outfile`: As a protobuf object to a particular file

There are then several options to control the default behaviour of the generator

- `--chars`: List the characters to be used in tree generation
- `--full-words`: Use only the start of each word and not every position within
- `--stats`: To report some simple statistics about the tree(s) generated

```txt
usage: langg generate [-h] [--json-out] [--json-outfile JSON_OUTFILE]
                      [--dot-out] [--dot-outfile DOT_OUTFILE]
                      [--proto-outfile PROTO_OUTFILE] [--separate-trees]
                      [--chars CHARS] [--root-chars ROOT_CHARS] [--full]
                      [-k KMERS] [-s]

optional arguments:
  -h, --help            show this help message and exit
  --json-out            Print JSON to stdout
  --json-outfile JSON_OUTFILE
                        Print JSON to given filename
  --dot-out             Print dotviz to stdout
  --dot-outfile DOT_OUTFILE
                        Print dotviz to given filename
  --proto-outfile PROTO_OUTFILE, --protobuf-outfile PROTO_OUTFILE
                        Print protobuf bin to given filename
  --separate-trees      Generate separate tree per dictionary file
  --chars CHARS, --considered-chars CHARS
                        Chars to consider in the dictionary files
  --root-chars ROOT_CHARS
                        Only process words starting with these chars
  --full, --full-words  Only add full words to the tree(s)
  -k KMERS, --kmers KMERS
                        Reports shound be made on k length substrings
  -s, --stats, --statistics
                        Print some tree stats to stdout

```

#### Translate

The `translate` subcommand has a few further input parameters as it needs to told what to translate, these include:

- `--stdin`: To read line by line from stdin and translate that with the provided tree
- `--txt`: Provide the string to translate directly in the command
- `--txt-in`: Provide the filename of a text file to translate

There is also `--seed` to override the default seed.

```txt
usage: langg translate [-h] (--stdin | --txt TXT | --txt-in txt_infiles) [-t TREE] [--seed SEED]
                       [--stdout] [--txt-outfile TXT_OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  --stdin               Read phrases to translate from stdin
  --txt TXT, --text TXT
                        String to translate
  --txt-in txt_infiles, --txt-infile txt_infiles
                        File to read and translate
  -t TREE, --tree TREE  Which tree in the input data to use
  --seed SEED           Seed to use in random number generation
  --stdout              Write translated phrases to stdout
  --txt-outfile TXT_OUTFILE
                        Print JSON to given filename
```

#### Bot

There are two important options here, if not provided each will take from an environment variable.

- `--token`: Is the Discord token needed to connect to the server (`DISCORD_BOT_TOKEN`)
- `--store-dir`: Is the directory where user trees and protobuf files will be written (`DISCORD_BOT_STORAGE_DIR`)

```txt
usage: langg bot [-h] [--token TOKEN] [--storage-dir STORAGE_DIR]

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         Supply the discord bot token
  --storage-dir STORAGE_DIR
                        Where to store uploaded dictionary files
```
