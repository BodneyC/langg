from __future__ import annotations

import os
import json

from ..translate.translator import Translator

USER_DATA_BASENAME: str = 'user-data.json'


class UserData:
    def __init__(self,
                 raw_fn: str = None,
                 proto_fn: str = None,
                 solved: dict = {},
                 translator: Translator = None):

        self.raw_fn: str = raw_fn
        self.proto_fn: str = proto_fn
        self.translator: Translator = translator

        self.solved: dict = solved

    @classmethod
    def from_dict(cls, d: dict) -> UserData:
        return UserData(
            raw_fn=d['raw_fn'],
            proto_fn=d['proto_fn'],
            solved=d['solved'])

    def dict_no_trn(self) -> dict:
        d: dict = self.__dict__.copy()
        del d['translator']
        return d

    def write(self) -> None:
        fn: str = os.path.join(
            os.path.dirname(self.raw_fn),
            USER_DATA_BASENAME)
        with open(fn, 'w') as f:
            f.write(json.dumps(self.dict_no_trn(), indent=2))
