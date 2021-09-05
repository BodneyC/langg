from discord import (Message, Attachment, Embed)
from discord.ext.commands import (
    CommandError, CommandNotFound, Context, Bot)

from .message_util import (MSG, EMBED)
from . import message_util as msg
from ..lib.ttop import TreeTop
from ..translate.translator import Translator
from ..util import namespace_ext as ns_ext
from ..util.cleaning_dict import TimingDict
from .user_data import (UserData, USER_DATA_BASENAME)

import os
import re
import json
import logging
from pathlib import Path
from types import SimpleNamespace

LOG: logging.Logger = logging.getLogger('bot')


class BotWrapper:
    def __init__(self, op_data: dict, command_prefix: str = '!'):
        self.bot = Bot(command_prefix=command_prefix, help_command=None)

        self.token: str = op_data.token or os.getenv('DISCORD_BOT_TOKEN')
        if not self.token:
            raise Exception('Discord bot token not provided')

        self.storage_dir: str = op_data.storage_dir or os.getenv(
            'DISCORD_BOT_STORAGE_DIR')
        if not self.storage_dir:
            raise Exception('Discord bot storage dir not provided')

        self.data: TimingDict[str, UserData] = TimingDict()

    def load_from_storage(self) -> None:
        log_prefix: str = 'load_from_storage:'
        LOG.info(f'{log_prefix} Loading data from storage')
        for root, dirs, _ in os.walk(self.storage_dir):
            for dir in dirs:
                username: str = str(dir)
                LOG.info(f'{log_prefix} Found data for {username}')

                user_data_fn: str = os.path.join(root, dir, USER_DATA_BASENAME)
                if not os.path.isfile(user_data_fn):
                    LOG.warn(f'{log_prefix} Data directory for {username} ' +
                             'contains no user data file')
                    continue

                with open(user_data_fn, 'r') as f:
                    user_data = UserData.from_dict(json.load(f))

                ttop: TreeTop = TreeTop.from_protobuf(user_data.proto_fn)
                if not ttop:
                    continue

                user_data.translator = Translator.for_bot(ttop, username)

                LOG.info(
                    f'{log_prefix} Successfully loaded data for {username}')

                self.data[username] = user_data

    def run(self) -> None:
        self.bot.run(self.token)

    ##########################################################################
    # Bot setup
    ##########################################################################

    def set_bot_commands(self) -> None:

        @self.bot.command(name='help', aliases=['h'])
        async def help(ctx: Context, *input):
            return await self.cmd_help(ctx, *input)

        @self.bot.command(name='dictionary', aliases=['d', 'dict', 'upload'])
        async def dictionary(*args, **kwargs) -> None:
            return await self.cmd_dictionary(*args, **kwargs)

        @self.bot.command(name='message', aliases=['m', 'mes'])
        async def message(*args, **kwargs) -> None:
            return await self.cmd_message(*args, **kwargs)

        @self.bot.command(name='solve', aliases=['s'])
        async def solve(*args, **kwargs) -> None:
            return await self.cmd_solve(*args, **kwargs)

        @self.bot.command(name='solved')
        async def solved(*args, **kwargs) -> None:
            return await self.cmd_voicesolved(*args, **kwargs)

        @self.bot.command(name='translate', aliases=['t', 'trn'])
        async def translate(*args, **kwargs) -> None:
            return await self.cmd_translate(*args, **kwargs)

    def set_bot_events(self):

        @self.bot.event
        async def on_command_error(ctx: Context, error: CommandError) -> None:
            log_prefix: str = f'on_command_error:{str(ctx.author)}:'
            LOG.warn(f'{log_prefix} Command error: {error}')

            cmds: [str] = [f'`{cmd.name}`' for cmd in self.bot.commands]
            cmds.sort()
            cmd_names: str = ', '.join(cmds)

            command_start: str = ctx.message.content.split()[0] + ' ...'

            embed = Embed(title='Langg Command Error',
                          description=msg.tag_author(ctx))
            if isinstance(error, CommandNotFound):
                embed.add_field(name='Command not found',
                                value=command_start, inline=False)
                embed.add_field(name='Available commands',
                                value=(MSG.errors
                                       .available_commands(cmd_names)),
                                inline=False)
            else:
                embed.add_field(name='Command in question',
                                value=command_start, inline=False)
                embed.add_field(name='Command error',
                                value=str(error), inline=False)
            await ctx.send(embed=embed)
            raise error

    def set_bot_listeners(self):

        async def on_message(message: Message):
            if message.author.id == self.bot.user.id:
                return
            if (message.content.startswith(self.bot.command_prefix)
                    and message.channel.type == 'dm'):
                await message.delete()

        self.bot.add_listener(on_message, 'on_message')

    ##########################################################################
    # Helpers
    ##########################################################################

    def _userhash_check_glob(self, userhash: str, _solved: dict) -> str:
        if '*' in userhash:
            userhash_glob: str = userhash.replace('*', '.*')
            userhash_re = re.compile(userhash_glob)
            for k in _solved.keys():
                if userhash_re.match(k):
                    userhash = k
        return userhash

    async def _tag_to_userhash(self, tag: str) -> str:
        untagged: str = msg.untag_user_id(tag)
        if not untagged.isnumeric():
            return untagged
        return str(await self.bot.fetch_user(untagged))

    async def cmd_help(self, ctx: Context, *input) -> None:
        embed = Embed(title='Langg Bot Help')
        for cmd in sorted(self.bot.commands, key=lambda c: c.name):
            if len(input) == 0 or (input[0] == cmd.name
                                   or input[0] in cmd.aliases):
                embed.add_field(name=cmd.name.capitalize(),
                                value=(MSG.info[cmd.name] +
                                       '\n\n' +
                                       MSG.help[cmd.name]),
                                inline=False)
        await ctx.send(embed=embed)

    ##########################################################################
    # Commands
    ##########################################################################

    async def cmd_dictionary(self, ctx: Context) -> None:
        username: str = str(ctx.author)
        log_prefix: str = f'cmd_dictionary:{username}:'

        attachments: [Attachment] = ctx.message.attachments

        if len(attachments) == 0:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.dictionary,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.no_attachment),
                    (EMBED.sub.help, MSG.help.dictionary)]))
            LOG.debug(f'{log_prefix} No attachment sent')
            return

        attachment: Attachment = attachments[0]

        path_fn: Path = (Path(self.storage_dir)
                         .joinpath(str(ctx.author))
                         .joinpath(attachment.filename))

        raw_fn: str = str(path_fn.with_suffix('.dict.txt'))
        os.makedirs(os.path.dirname(raw_fn), exist_ok=True)

        await attachment.save(raw_fn)
        LOG.info(f'{log_prefix} Attachment saved to: {raw_fn}')

        ttop = TreeTop.for_bot(raw_fn)
        LOG.info(f'{log_prefix} TreeTop created')
        ttop.parse_infiles()
        LOG.info(f'{log_prefix} Infiles parsed')
        ttop.sort_trees()

        proto_fn: str = str(path_fn.with_suffix('.proto'))

        ttop.write_protobuf(proto_fn)
        LOG.info(f'{log_prefix} Protobuf written to: {proto_fn}')

        translator = Translator.for_bot(ttop, username)

        if username in self.data:
            LOG.info(f'Removing solved data for {username}')
            await ctx.send(embed=msg.embed(
                title=EMBED.title.dictionary,
                desc=MSG.tag.everyone,
                fields=[(EMBED.sub.warning,
                         MSG.errors.abandon(msg.tag_author(ctx)))]))
            for k, v in self.data.items():
                if k == username:
                    continue
                if v and v.solved and k in v.solved:
                    LOG.debug(f'{k} had solved words for {username}')
                    v.solved[k] = {}

        self.data[username] = UserData(
            raw_fn=raw_fn, proto_fn=proto_fn, translator=translator)
        LOG.info(f'{log_prefix} UserData loaded')

        self.data[username].write()
        LOG.info(f'{log_prefix} UserData written')

        await ctx.send(embed=msg.embed(
            title=EMBED.title.dictionary,
            desc=msg.tag_author(ctx),
            fields=[(EMBED.sub.status, MSG.data.upload)]))

    async def cmd_message(self, ctx: Context) -> None:
        username: str = str(ctx.author)
        log_prefix: str = f'cmd_message:{username}'
        cmd_parts = ctx.message.content.split(' ', 1)

        if len(cmd_parts) != 2:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.message,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.no_message),
                    (EMBED.sub.help, MSG.help.message)]))
            LOG.debug(f'{log_prefix} User {ctx.author} ' +
                      'did not send a message')
            return

        if username not in self.data or not self.data[username].translator:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.message,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.data.no_dict),
                    (EMBED.sub.help, MSG.help.message)]))
            LOG.debug(f'{log_prefix} Has not created a dictionary')
            return

        message: str = cmd_parts[1]

        sto: str = self.data[username].translator.translate_text(message)
        LOG.debug(f'{log_prefix} Message to be sent {sto}')

        await ctx.send(embed=msg.embed(
            title=EMBED.title.message,
            desc=msg.tag_author(ctx),
            fields=[(EMBED.sub.message, sto)]))

    async def cmd_solve(self, ctx: Context) -> None:
        username: str = str(ctx.author)
        log_prefix: str = f'cmd_solve:{username}'
        cmd_parts: [str] = ctx.message.content.split()

        if username not in self.data:
            self.data[username] = UserData()

        _solved: dict = self.data[username].solved

        if (len(cmd_parts) != 4):
            await ctx.send(embed=msg.embed(
                title=EMBED.title.solve,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.invalid_args),
                    (EMBED.sub.help, MSG.help.solve)]))
            LOG.info(f'{log_prefix} Invalid cmd: {cmd_parts[1:]}')
            return

        tag, wfrom, wto = cmd_parts[1:]

        userhash = self._userhash_check_glob(
            await self._tag_to_userhash(tag),
            _solved)

        if '#' not in userhash:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.solve,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.invalid_userhash(userhash)),
                    (EMBED.sub.help, MSG.help.solve)]))
            LOG.info(f'{log_prefix} Userhash ({userhash}) is not valid')
            return

        if userhash not in self.data:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.solve,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.solve_for(userhash)),
                    (EMBED.sub.help, MSG.help.solve)]))
            LOG.info(f'{log_prefix} Specified user ({userhash}) has no data')
            return

        if userhash not in _solved:
            _solved[userhash] = {}

        _solved[userhash][wfrom] = wto

        await ctx.send(embed=msg.embed(
            title=EMBED.title.solve,
            desc=MSG.tag.everyone,
            fields=[(EMBED.sub.solved,
                     (msg.tag_author(ctx) + ' ' +
                      "thinks they've solved a word!"))]))

        self.data[username].write()
        LOG.info(f'{log_prefix} UserData written')

    async def cmd_solved(self, ctx: Context) -> None:
        username: str = str(ctx.author)
        log_prefix: str = f'cmd_solve:{username}'
        cmd_parts: [str] = ctx.message.content.split()

        if username not in self.data:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.solved,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.no_data),
                    (EMBED.sub.help, MSG.help.solve)]))
            LOG.info(f'{log_prefix} Attempt to dump solved with no data')
            return

        _solved: dict = self.data[username].solved
        if len(cmd_parts) == 0:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.solved,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.invalid_args),
                    (EMBED.sub.help, MSG.help.solve)]))
            return

        if len(cmd_parts) == 1:
            await ctx.author.send(embed=msg.embed(
                title=EMBED.title.solved,
                fields=[(EMBED.sub.solved, msg.json_code_block(_solved))]))
            return

        userhash = self._userhash_check_glob(
            await self._tag_to_userhash(cmd_parts[1]),
            _solved)

        if '#' not in userhash:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.solved,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.invalid_userhash(userhash)),
                    (EMBED.sub.help, MSG.help.solve)]))
            LOG.info(f'{log_prefix} Userhash ({userhash}) is not valid')
            return

        if userhash not in _solved:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.solved,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.non_solved(userhash)),
                    (EMBED.sub.help, MSG.help.solve)]))
            LOG.info(f'{log_prefix} None yet solved for user {userhash}')
            return

        if len(cmd_parts) == 2:
            solved_block: str = msg.json_code_block(
                {userhash: _solved[userhash]})
            await ctx.author.send(embed=msg.embed(
                title=EMBED.title.solved,
                fields=[('Solved', solved_block)]))

        elif len(cmd_parts) == 3:
            word: str = cmd_parts[2]
            if word not in _solved[userhash]:
                await ctx.send(embed=msg.embed(
                    title=EMBED.title.solved,
                    desc=msg.tag_author(ctx),
                    fields=[
                        (EMBED.sub.error,
                            MSG.errors.word_not_solved(userhash, word)),
                        (EMBED.sub.help, MSG.help.solve)]))
                LOG.info(f'{log_prefix} Word ({word}) not yet solved for '
                         f'user {userhash}')
                return

            solved_block: str = msg.json_code_block({
                userhash: {k: v for k, v in _solved[userhash].items()
                           if k == word}})

            await ctx.author.send(embed=msg.embed(
                title=EMBED.title.solved,
                fields=[('Solved', solved_block)]))

    async def cmd_translate(self, ctx: Context) -> None:
        username: str = str(ctx.author)
        log_prefix: str = f'cmd_message:{username}'
        cmd_parts = ctx.message.content.split(None, 2)

        if len(cmd_parts) != 3:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.translate,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.invalid_args),
                    (EMBED.sub.help, MSG.help.translate)]))
            LOG.debug(f'{log_prefix} Invalid command: {ctx.message.content}')
            return

        if username not in self.data:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.translate,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.no_dict),
                    (EMBED.sub.help, MSG.help.translate)]))
            LOG.debug(f'{log_prefix} Has not created a dictionary')
            return

        _solved: dict = self.data[username].solved

        userhash = self._userhash_check_glob(
            await self._tag_to_userhash(cmd_parts[1]),
            _solved)

        if '#' not in userhash:
            await ctx.send(embed=msg.embed(
                title=EMBED.title.translate,
                desc=msg.tag_author(ctx),
                fields=[
                    (EMBED.sub.error, MSG.errors.invalid_userhash(userhash)),
                    (EMBED.sub.help, MSG.help.translate)]))
            LOG.info(f'{log_prefix} Userhash ({userhash}) is not valid')
            return

        sfrom: str = cmd_parts[2]
        sto: str = ''
        if userhash in _solved:
            for wfrom, wto in _solved[userhash].items():
                wfrom_re: re.Pattern = re.compile(
                    f'(^| )({wfrom})( |$)', re.IGNORECASE)
                ridx: int = 0
                for match in wfrom_re.finditer(sfrom):
                    # Note: `2` for middle group in the regex
                    span: (int, int) = match.span(2)
                    sto += sfrom[ridx:span[0]]
                    orig_word: str = sfrom[span[0]:span[1]]

                    ridx = span[1]

                    upper_idx_pos: [float] = [
                        i / len(orig_word) for i in range(len(orig_word))
                        if orig_word[i].isupper()]

                    for pos in upper_idx_pos:
                        new_pos: int = int(pos * len(wto))
                        wto = wto[:new_pos] + wto[new_pos].upper() + \
                            wto[new_pos + 1:]

                    sto += msg.bold(wto)
                sto += sfrom[ridx: len(sfrom)]

        if sto == '':
            sto = sfrom

        await ctx.author.send(embed=msg.embed(
            title=EMBED.title.translate,
            fields=[
                (EMBED.sub.original, sfrom),
                (EMBED.sub.translated, sto)]))


def run(args_dict: dict) -> None:
    args: SimpleNamespace = ns_ext.wrap_namespace(args_dict)

    bot = BotWrapper(args.op_data)

    bot.load_from_storage()

    bot.set_bot_commands()
    bot.set_bot_events()
    bot.set_bot_listeners()

    LOG.info('Started, awaiting input...')

    bot.run()  # Blocks

    bot.data.timer.cancel()
