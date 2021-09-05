#!/usr/bin/env python3

from .util import argp

import os
import sys
import signal
import logging as log


__version__ = '0.0.1'


def sigint(sig, frame):
    print('Signal received, exiting')
    sys.exit(130)


def main():
    parser = argp.parser()

    try:
        _args = parser.parse_args()
    except Exception:
        parser.print_help()
        sys.exit(0)

    log.basicConfig(level=(os.getenv('LOG_LEVEL') or _args.log).upper())

    args = vars(_args)

    signal.signal(signal.SIGINT, sigint)

    if args['cmd'] == 'bot':
        from .bot import bot
        bot.run(args)
    else:
        from .lib import langg
        langg.run(args)


if __name__ == '__main__':
    main()
