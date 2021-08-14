#!/usr/bin/env python3

from .util import argp
from .lib.langg import run

import os
import logging as log


__version__ = '0.0.1'

if __name__ == '__main__':
    _args = argp.parse_args()
    log.basicConfig(level=(os.getenv('LOG_LEVEL') or _args.log).upper())
    args = vars(_args)
    run(args)
