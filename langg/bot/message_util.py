from discord.ext.commands import Context

from ..util.namespace import Namespace

import json

MSG = Namespace(
    tag=Namespace(everyone='@everyone', here='@here'),
    help=Namespace(
        _invalid='Available commands: ',
        message='!message Message contents...',
        dictionary='!dictionary <file upload>',
        solve='!solve userhash in-langg in-english',
        solved='!solved [userhash]',
        translate='!translate userhash Message to translate...',
    ),
    errors=Namespace(
        solve_for=(
            lambda u: f'Cannot solve for user ({u}) '
            'who has no data'),
        no_data='You have no data',
        non_solved=lambda u: f"Nothing solved for user ({u})",
        word_not_solved=lambda u, w: f'Word ({w}) not solved for user ({u})',
        invalid_userhash=lambda u: f'Invalid userhash ({u})',
    ),
    data=Namespace(
        no_dict='No dictionary loaded for user',
        abandon=' has abandoned their dictionary, all your solved words ' +
        'are now void',
        upload='Dictionary has been uploaded',
    ),
)


def json_code_block(d: dict) -> str:
    return f'```json\n{json.dumps(d, indent=2)}\n```'


def username_no_hash(ctx: Context):
    return str(ctx.author).split('#')[0]


def tag_user_string(ctx: Context):
    return f'<@{ctx.author.id}>'


def untag_user_id(s: str):
    if s.startswith('<@!'):
        return s[3:-1]
    return s
