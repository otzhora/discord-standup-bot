import asyncio
from collections.abc import Sequence

from discord.ext import commands


def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)


def message_check(channel=None, author=None, content=None, ignore_bot=True, lower=True):
    channel = make_sequence(channel)
    author = make_sequence(author)
    content = make_sequence(content)
    if lower:
        content = tuple(c.lower() for c in content)

    def check(message):
        if ignore_bot and message.author.bot:
            return False
        if channel and message.channel not in channel:
            return False
        if author and message.author not in author:
            return False
        actual_content = message.content.lower() if lower else message.content
        if content and actual_content not in content:
            return False
        return True

    return check


class StandupBot(commands.Bot):
    def __init__(self, GUILD, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.users_storage = {}  # TODO: create proper storage
        self.standup_channel = None
        self.bg_work = self.loop.create_task(self.collect_standups())
        self.works = []
        self.GUILD = GUILD

    async def on_ready(self):
        channels = None
        for guild in self.guilds:
            if guild.name == self.GUILD:
                channels = guild.channels

        for ch in channels:
            if ch.name == "standups":
                self.standup_channel = ch

    async def collect_standup_from_user(self, user):
        await user.create_dm()

        await user.dm_channel.send(f"What did you do yesterday?")
        done_tasks = await self.wait_for('message',
                                         check=message_check(
                                             channel=user.dm_channel),
                                         timeout=12 * 60 * 60)
        await user.dm_channel.send(f"What do you want to do today?")
        future_tasks = await self.wait_for('message',
                                           check=message_check(
                                               channel=user.dm_channel),
                                           timeout=12 * 60 * 60)
        await user.dm_channel.send(f"Any problems?")
        problems = await self.wait_for('message',
                                       check=message_check(
                                           channel=user.dm_channel),
                                       timeout=12 * 60 * 60)
        response = f"\n\nHey! <@{user.id}> posted a standup:\n\n" \
                   f"What did you do yesterday?\n" \
                   f"```md\n" \
                   f"{done_tasks.content}\n" \
                   f"```" \
                   f"What do you want to do today?\n" \
                   f"```md\n" \
                   f"{future_tasks.content}" \
                   f"```" \
                   f"Any problems?\n" \
                   f"```md\n" \
                   f"{problems.content}\n" \
                   f"```"
        await self.standup_channel.send(response)

    async def collect_standups(self):
        await self.wait_until_ready()

        while not self.is_closed():
            for user in self.users_storage.values():
                self.works.append(self.loop.create_task(
                    self.collect_standup_from_user(user)))
            await asyncio.sleep(24 * 60 * 60)

            for work in self.works:
                work.cancel()

    async def on_error(self, event, *args, **kwargs):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise


class Register(commands.Cog):
    def __init__(self, bot_to_attach):
        self.bot = bot_to_attach

    @commands.command(help='Commit to writing standups')
    @commands.has_any_role("гей", "slave master")
    async def register(self, ctx):
        if ctx.author.id in self.bot.users_storage:
            await ctx.send("You are already registered")
            return
        self.bot.users_storage[ctx.author.id] = ctx.author
        self.bot.works.append(self.bot.loop.create_task(
            self.bot.collect_standup_from_user(ctx.author)))

        await ctx.send("You are committed to writing standups")



