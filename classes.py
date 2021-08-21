from typing import List, Union, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClient
from discord.ext import commands
from discord_slash import SlashCommand

import os
import aiohttp


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.token = None
        self.auth = None
        self.api = f"https://discord.com/api/v{kwargs.pop('api_version_number', 9)}/"
        super().__init__(*args, **kwargs)
        self.db_url = kwargs.get("db_url")  # AsyncIOMotorClient(os.getenv("DB_URL"))
        self.slash = SlashCommand(
            self,
            sync_commands=True,
            sync_on_cog_reload=True,
            application_id=kwargs["app_id"]
        )

    def run(self, *args, **kwargs):
        self.token = args[0]
        self.auth = {"Authorization": f"Bot {self.token}"}
        # self.clear_slashes()
        super().run(*args, **kwargs)


class Database:
    def __init__(self, db_url):
        self.db_url = db_url  # db.timezones.get_collection("timezones")

    async def exists(self, user_id: int) -> bool:
        collection = self.con.timekeeper.get_collection("timezone")
        return bool(await collection.count_documents({"_id": user_id}))

    async def get(self, user_id: int) -> Optional[Tuple[int, int]]:
        collection = self.con.timekeeper.get_collection("timezone")
        doc = await collection.find_one({"_id": user_id})
        return doc["hours"], doc["minutes"]

    async def set(self, user_id: int, d_hours: int, d_minutes: int):
        collection = self.con.timekeeper.get_collection("timezone")
        print("HI")
        # print(d_hours, d_minutes)
        new_doc = {
            "_id": user_id,
            "hours": d_hours,
            "minutes": d_minutes
        }
        x = await collection.find_one_and_replace({"_id": user_id}, new_doc)
        print(x, new_doc)
        if not x:
            print("LMAO")
            await collection.insert_one(new_doc)

    async def __aenter__(self) -> 'Database':
        self.con = AsyncIOMotorClient(os.getenv("DB_URL"))
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        self.con.close()
        pass


class APIBuilder:
    def __init__(self):
        self.requests = []

    class SendMessage:
        pass

    def sendMessage(self, content, *, embed=None, ):
        return self


class Request:
    @staticmethod
    async def get(urls: Union[List[str], str], *, headers=None):
        if isinstance(urls, str): urls = [urls]
        session = aiohttp.ClientSession()
        return [await session.get(url, headers=headers) for url in urls]

    @staticmethod
    async def delete(urls: Union[List[str], str], *, headers=None):
        if isinstance(urls, str): urls = [urls]
        session = aiohttp.ClientSession()
        return [await session.delete(url, headers=headers) for url in urls]

