import os
import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "dedpost")
mongo = AsyncIOMotorClient(MONGO_URI)
db = mongo[DB_NAME]
settings_db = db.settings


async def send_webhook_report(webhook_url, user, channel, total_msg, delay, next_post, status, device, uptime, thumb):
    color = 0x2ecc71 if status.lower() == "success" else 0xe74c3c
    
    data = {
        "username": "AutoPost Logger",
        "avatar_url": thumb,
        "embeds": [{
            "title": "📢 AUTO POST REPORT",
            "color": color,
            "thumbnail": {"url": thumb},
            "fields": [
                {"name": "👤 USER", "value": user, "inline": False},
                {"name": "🌐 CHANNEL", "value": channel, "inline": False},
                {"name": "💬 TOTAL MESSAGE", "value": str(total_msg), "inline": False},
                {"name": "😴 DELAY", "value": f"{delay} minutes", "inline": False},
                {"name": "✉ NEXT POST", "value": next_post, "inline": False},
                {"name": "❓ STATUS", "value": status.upper(), "inline": False},
                {"name": "🖥 DEVICE", "value": device, "inline": False},
                {"name": "⏱ UPTIME", "value": uptime, "inline": False},
            ]
        }]
    }

    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json=data)


async def autopost_worker():
    while True:
        async for st in settings_db.find({"active": True}):
            print("Running autopost for guild:", st["guild_id"])

            webhook = st.get("webhook")
            if webhook:
                await send_webhook_report(
                    webhook_url=webhook,
                    user="User Example",
                    channel=f"<#{st.get('channel_id')}>",
                    total_msg=999,
                    delay=st.get("delay"),
                    next_post="Now",
                    status="Success",
                    device="Discord Bot",
                    uptime="1h 22m 10s",
                    thumb="https://cdn.discordapp.com/embed/avatars/3.png"
                )

        await asyncio.sleep(5)


asyncio.run(autopost_worker())