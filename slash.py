import json
import os
import requests
import dotenv

dotenv.load_dotenv()


api = f"https://discord.com/api/v9/"
token = os.getenv("TOKEN")
app_id = os.getenv("APP_ID")


headers = {
    "Authorization": f"Bot {token}"
}

guilds = [_["id"] for _ in requests.get(api + f"users/@me/guilds", headers=headers).json()]
print(guilds)

guilds_with_slash_commands = [_ for _ in guilds if requests.get(api + f"applications/{app_id}/guilds/{_}/commands", headers=headers).json()]
print(guilds_with_slash_commands)

resp = requests.get(api + f"applications/{app_id}/commands", headers=headers)
print("GLOBAL\n", len(resp.json()))

for guild_id in guilds_with_slash_commands:
    resp = requests.get(api + f"applications/{app_id}/guilds/{guild_id}/commands", headers=headers)
    print(f"{guild_id}\n", len(resp.json()))
    print((resp.json()))


exit()
if True:
    # GLOBAL
    slashes = requests.get(api+f"applications/{app_id}/commands", headers=headers).json()
    for slash in slashes:
        requests.delete(api+f"applications/{slash['application_id']}/commands/{slash['id']}", headers=headers)

    # GUILD
    for guild_id in guilds_with_slash_commands:
        slashes = requests.get(api+f"applications/{app_id}/guilds/{guild_id}/commands", headers=headers).json()
        for slash in slashes:
            r = requests.delete(api + f"applications/{app_id}/guilds/{guild_id}/commands/{slash['id']}", headers=headers)
