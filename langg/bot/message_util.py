from discord import Embed
from discord.embeds import EmptyEmbed
from discord.ext.commands import Context

from ..util.namespace import Namespace

import json
from typing import Optional

EMBED = Namespace(
    title=Namespace(
        help='Langg Help',
        message='Langg Message',
        dictionary='Langg Dictionary/upload',
        solve='Langg Solve',
        solved='Langg Solved',
        translate='Langg Translate',
    ),
    sub=Namespace(
        error='Error',
        help='Help',
        warning='Warning',
        status='Status',
        message='Message',
        solved='Solved',
        original='Original',
        translated='Translated',
    ),
)

MSG = Namespace(
    tag=Namespace(everyone='@everyone', here='@here'),
    help=Namespace(
        help='`!help [subcommand]`',
        message='`![m|mes|message] <Message contents...>`',
        dictionary='`![d|dict|dictionary|upload] <file upload>`',
        solve='`![s|solve] <userhash> <in-langg> <in-english>`',
        solved='`!solved [userhash]`',
        translate='`![t|trn|translate] <userhash> <Message to translate...>`',
    ),
    info=Namespace(
        help='Show a similar message to this one',
        message='Send a message using a language built from your dictionary',
        dictionary='Upload a dictionary file to be processed for your user',
        solve='Solve a word in the given user\'s language',
        solved='Show words that you have solved (in a DM)',
        translate='Translate a phrase using your solved words for a given ' +
        'user',
    ),
    errors=Namespace(
        available_commands=lambda s: f'Available commands: {s}',
        solve_for=lambda u: f'Cannot solve for user ({u}) who has no data',
        non_solved=lambda u: f"Nothing solved for user ({u})",
        word_not_solved=lambda u, w: f'Word ({w}) not solved for user ({u})',
        invalid_userhash=lambda u: f'Invalid userhash ({u})',
        no_data='You have no data',
        invalid_args='Invalid number of arguments',
        no_attachment='No attachment in command',
        no_message='No message to send provided',
    ),
    data=Namespace(
        no_dict='No dictionary loaded for user',
        abandon=lambda u: (f'{u} has abandoned their dictionary, all your ' +
                           'solved words are now void'),
        upload='Dictionary has been uploaded',
    ),
)


def embed(title: str,
          desc: Optional[str] = EmptyEmbed,
          color: Optional[str] = EmptyEmbed,
          fields: [(str, str, Optional[bool])] = []) -> Embed:
    _embed = Embed(title=title, description=desc, color=color)
    for field in fields:
        inline: bool = False if len(field) < 3 else field[2]
        _embed.add_field(name=field[0], value=field[1], inline=inline)
    return _embed


def italicize(s: str) -> str:
    return f'*{s}*'


def bold(s: str) -> str:
    return f'**{s}**'


def json_code_block(d: dict) -> str:
    return f'```json\n{json.dumps(d, indent=2)}\n```'


def username_no_hash(ctx: Context):
    return str(ctx.author).split('#')[0]


def tag_author(ctx: Context):
    return f'<@{ctx.author.id}>'


def untag_user_id(s: str):
    if s.startswith('<@!'):
        return s[3:-1]
    return s
