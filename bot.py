import os
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from pymongo import MongoClient

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

mongo = MongoClient(MONGO)
db = mongo[DB_NAME]
accounts = db["accounts"]


class PanelButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="⚙ Settings", style=nextcord.ButtonStyle.primary)
    async def settings(self, button, interaction: Interaction):
        await interaction.response.send_message(
            "Setting panel opened",
            ephemeral=True
        )


@bot.slash_command(name="panel", description="Open autopost panel")
async def panel(interaction: Interaction):
    embed = nextcord.Embed(
        title="🚀 DedPost Premium Panel",
        description="Panel autopost mix premium style.",
        color=nextcord.Color.blurple()
    )
    embed.set_thumbnail(url="https://i.imgur.com/5fX8G0S.png")

    await interaction.response.send_message(
        embed=embed,
        view=PanelButton(),
        ephemeral=True
    )


@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")
    try:
        synced = await bot.sync_application_commands()
        print(f"Command synced: {len(synced)}")
    except Exception as e:
        print("Error syncing:", e)

bot.run(TOKEN)
