import os
import asyncio
import requests
from pymongo import MongoClient

MONGO = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

mongo = MongoClient(MONGO)
db = mongo[DB_NAME]
accounts = db["accounts"]

async def autopost_loop():
    while True:
        for acc in accounts.find({"active": True}):
            try:
                headers = {"authorization": acc["token"]}
                data = {"content": acc["message"]}

                requests.post(
                    f"https://discord.com/api/v9/channels/{acc['channel_id']}/messages",
                    json=data,
                    headers=headers
                )

                if acc.get("webhook"):
                    requests.post(
                        acc["webhook"],
                        json={
                            "embeds": [
                                {
                                    "title": "💬 Autopost Success",
                                    "description": f"Message terkirim ke <#{acc['channel_id']}>",
                                    "color": 65280,
                                    "thumbnail": {"url": "https://i.imgur.com/MQszDqP.png"},
                                }
                            ]
                        }
                    )

                print("Post sent:", acc["user_id"])

            except Exception as e:
                print("Error posting:", e)

            await asyncio.sleep(acc["delay"])

        await asyncio.sleep(1)

asyncio.run(autopost_loop())
