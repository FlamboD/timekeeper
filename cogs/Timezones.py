from classes import Bot, Database
from datetime import datetime, timedelta
from discord.ext import commands
from discord_slash import (
    SlashContext,
    cog_ext,
    ButtonStyle,
    ComponentContext
)
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button
)
from typing import Union

# import aiosqlite
import discord
import re


guild_ids = [545154538852843534, 618520031210373141, 877451789618798612]


def pad(_int: Union[str, int]) -> str:
    return f"00{int(_int)}"[-2:]


def td_hm(td: timedelta) -> (int, int):
    hour = td.total_seconds()//3600 % 24
    minute = td.total_seconds()//60 % 60
    return int(hour), int(minute)


class Timezones(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @cog_ext.cog_slash(
        description="Set your timezone. Enter your current time in `HH:MM` 24-hour format.",
        guild_ids=guild_ids
    )
    async def timezone(self, ctx: SlashContext, current_time: str):
        if not re.match("^[0-2]?[0-9]:[0-5]?[0-9]$", current_time):
            return await ctx.send(
                f"Invalid time format entered. Enter your current time in `HH:MM` 24-hour format. (You entered: {current_time})",
                hidden=True
            )
        hour, minute = map(int, current_time.split(":"))
        now = datetime.utcnow()

        d_hours = (hour - now.hour) % 24
        d_minutes = (minute - now.minute) % 60

        async with Database(self.bot.db_url) as db:
            await db.set(ctx.author_id, d_hours, d_minutes)

        await ctx.reply("Your timezone has been set successfully.", hidden=True)

    @cog_ext.cog_slash(
        description="Display a time. Enter a time in `HH:MM` 24-hour format.",
        guild_ids=guild_ids
    )
    async def time(self, ctx: SlashContext, time: str, message: str = "Time"):
        async with Database(self.bot.db_url) as db:
            if not await db.exists(ctx.author_id):
                return await ctx.send(
                    "Use the `/timezone` command to set your timezone before you use this command.",
                    hidden=True
                )
            else:
                d_hours, d_minutes = await db.get(ctx.author_id)  # Author
        if not re.match("^[0-2]?[0-9]:[0-5]?[0-9]$", time):
            return await ctx.send(
                f"Invalid time format entered. Enter your desired time in `HH:MM` 24-hour format. (You entered: {time})",
                hidden=True
            )
        hour, minute = map(int, time.split(":"))  # Given

        td = timedelta(hours=d_hours, minutes=d_minutes)
        utc_time = timedelta(hours=hour, minutes=minute) - td
        utc_hour, utc_minute = td_hm(utc_time)
        button = create_button(ButtonStyle.blue, "Convert time", custom_id=f"{utc_hour}:{utc_minute}")
        ar = create_actionrow(button)
        embed = discord.Embed(title=f"Time: {pad(hour)}:{pad(minute)}")
        embed.set_author(name=message)
        embed.set_footer(text=f"{pad(utc_hour)}:{pad(utc_minute)} UTC")
        await ctx.reply(
            embed=embed,
            components=[ar]
        )

    @commands.Cog.listener()
    async def on_component(self, interaction: ComponentContext):
        async with Database(self.bot.db_url) as db:
            if not await db.exists(interaction.author.id):
                try:
                    return await interaction.reply(
                        content="Use the `/timezone` command to set your timezone before you use this command.",
                        hidden=True
                    )
                except discord.NotFound:
                    return
            else:
                d_hours, d_minutes = await db.get(interaction.author.id)
        ad_hours, ad_minutes = map(int, interaction.custom_id.split(":"))
        c_hour, c_minute = td_hm(timedelta(hours=ad_hours, minutes=ad_minutes) + timedelta(hours=d_hours, minutes=d_minutes))
        c_now = datetime.utcnow() + timedelta(hours=d_hours, minutes=d_minutes)
        try:
            await interaction.reply(
                content=f"`{pad(c_hour)}:{pad(c_minute)}` your time. (If your current time isn't `{pad(c_now.hour)}:{pad(c_now.minute)}` use `/timezone` to reset it)",
                hidden=True
            )
        except discord.NotFound: pass


def setup(bot: Bot):
    bot.add_cog(Timezones(bot))
