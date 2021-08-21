import discord
import os
from classes import Bot
import dotenv

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.members = True
bot = Bot(
    "!",
    case_insensitive=True,
    intents=intents,
    api_version_number=9,
    app_id=os.getenv("APP_ID"),
    db_url=os.getenv("DB_URL")
)

@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f"Joined {guild.name}")


for cog in os.listdir("cogs"):
    if cog.endswith(".py") and not cog.startswith("-"):
        print(f'Adding cog {cog[:-3]}')
        bot.load_extension(f"cogs.{cog[:-3]}")

bot.run(os.getenv("TOKEN"))
