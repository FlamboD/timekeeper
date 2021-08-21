from discord.ext import commands
import discord
import settings
import aiohttp


async def request_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.content.read()


def user_check(ctx: commands.Context):
    data: dict = settings.load()
    return ctx.author.id in (data["allowed_users"], 211897824135086080)


def channel_check(ctx: commands.Context):
    data: dict = settings.load()
    return ctx.channel.id not in data["blocked_channels"] or str(ctx.command) in ("channel", "channel enable")


@commands.check(user_check)
class BotController(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return user_check(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        settings.setup()
        self.bot.add_check(channel_check)
        print("Hi")
        pass

    @commands.command()
    async def nick(self, ctx: commands.Context, *, nick=None):
        me: discord.Member = ctx.guild.get_member(self.bot.user.id)
        if not nick:
            return await ctx.send(me.display_name)
        await me.edit(nick=nick)

    @commands.command()
    async def pfp(self, ctx: commands.Context, url=None):
        if not any([url, ctx.message.attachments]):
            return await ctx.send("Error: No image attached")
        with ctx.channel.typing():
            img = await request_image(url) if url else await ctx.message.attachments[0].read()
            size = len(img)*1e-6
            if size > 8: return await ctx.send(f"Image size({round(size, 2)}MB) is too large")
            await self.bot.user.edit(avatar=img)
        await ctx.send("Avatar updated")

    @commands.group()
    async def prefix(self, ctx: commands.Context): pass

    @prefix.command()
    async def list(self, ctx: commands.Context):
        await ctx.send(", ".join(f"`{_}`" if not _ == self.bot.user.mention else _ for _ in self.bot.command_prefix(self.bot, ctx.message)))

    @prefix.command()
    async def add(self, ctx: commands.Context, prefix: str):
        data: dict = settings.load()
        prefixes = set(data["prefix"])
        if prefix in prefixes: return await ctx.send(f"Prefix `{prefix}` already exists")
        prefixes.add(prefix)
        data["prefix"] = list(prefixes)
        settings.dump(data)
        await ctx.send(f"Prefix `{prefix}` has been added")

    @prefix.command()
    async def remove(self, ctx: commands.Context, prefix: str):
        data: dict = settings.load()
        prefixes = set(data["prefix"])
        if prefix not in prefixes: return await ctx.send(f"Prefix `{prefix}` not in prefix list")
        prefixes.remove(prefix)
        data["prefix"] = list(prefixes)
        settings.dump(data)
        await ctx.send(f"Prefix `{prefix}` has been removed")

    @commands.group()
    async def channel(self, ctx: commands.Context): pass

    @channel.command()
    async def enable(self, ctx: commands.Context):
        data: dict = settings.load()
        blocked_channels = set(data["blocked_channels"])
        if ctx.channel.id not in blocked_channels: return await ctx.send(f"This channel is already enabled")
        blocked_channels.remove(ctx.channel.id)
        data["blocked_channels"] = list(blocked_channels)
        settings.dump(data)
        await ctx.send(f"This channel has been enabled")

    @channel.command()
    async def disable(self, ctx: commands.Context):
        data: dict = settings.load()
        blocked_channels = set(data["blocked_channels"])
        if ctx.channel.id in blocked_channels: return await ctx.send(f"This channel is already blocked")
        blocked_channels.add(ctx.channel.id)
        data["blocked_channels"] = list(blocked_channels)
        settings.dump(data)
        await ctx.send(f"This channel has been blocked")


def setup(bot: commands.Bot):
    bot.add_cog(BotController(bot))
