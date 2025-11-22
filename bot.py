import os
import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

mongo = MongoClient(MONGO)
db = mongo[DB_NAME]
accounts = db["accounts"]

# ================================
# BUTTONS + PANEL (MIX STYLE)
# ================================
class PanelButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚙ Settings", style=discord.ButtonStyle.primary)
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="⚙ Settings Panel",
                description="Isi data autopost kamu di bawah ini.",
                color=discord.Color.blue(),
            ),
            view=SettingsForm(),
            ephemeral=True
        )

    @discord.ui.button(label="👤 Account Manager", style=discord.ButtonStyle.secondary)
    async def account(self, interaction: discord.Interaction, button: discord.ui.Button):
        doc = accounts.find_one({"user_id": interaction.user.id})

        if not doc:
            return await interaction.response.send_message("Belum ada akun diset!", ephemeral=True)

        embed = discord.Embed(
            title="👤 Account Info",
            description=f"**Token:** {doc['token'][:20]}****\n"
                        f"**Delay:** {doc['delay']} detik\n"
                        f"**Channel:** {doc['channel_id']}\n"
                        f"**Message:** {doc['message']}\n"
                        f"**Webhook:** {doc.get('webhook', '-')}",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url="https://i.imgur.com/MQszDqP.png")  # thumbnail premium

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🚀 Start", style=discord.ButtonStyle.success)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        accounts.update_one(
            {"user_id": interaction.user.id},
            {"$set": {"active": True}},
            upsert=True
        )

        await interaction.response.send_message("Autopost **diaktifkan** ✔", ephemeral=True)

    @discord.ui.button(label="🛑 Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        accounts.update_one(
            {"user_id": interaction.user.id},
            {"$set": {"active": False}},
            upsert=True
        )

        await interaction.response.send_message("Autopost **dimatikan** ❌", ephemeral=True)


# =============================
# SETTINGS FORM (INPUT DATA)
# =============================
class SettingsForm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.token = discord.ui.TextInput(label="Token User")
        self.message = discord.ui.TextInput(label="Message Autopost", style=discord.TextStyle.long)
        self.delay = discord.ui.TextInput(label="Delay (detik)")
        self.channel = discord.ui.TextInput(label="Channel ID")
        self.webhook = discord.ui.TextInput(label="Webhook URL (optional)")

        self.add_item(self.token)
        self.add_item(self.message)
        self.add_item(self.delay)
        self.add_item(self.channel)
        self.add_item(self.webhook)

    @discord.ui.button(label="💾 Save", style=discord.ButtonStyle.success)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        accounts.update_one(
            {"user_id": interaction.user.id},
            {
                "$set": {
                    "token": self.token.value,
                    "message": self.message.value,
                    "delay": int(self.delay.value),
                    "channel_id": int(self.channel.value),
                    "webhook": self.webhook.value,
                    "active": False
                }
            },
            upsert=True
        )

        await interaction.response.send_message("Data berhasil disimpan ✔", ephemeral=True)


# =============================
# SLASH COMMAND: /panel
# =============================
@bot.tree.command(name="panel", description="Buka panel autopost premium")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🚀 DedPost Premium Panel",
        description="Gunakan tombol di bawah untuk mengatur autopost kamu.",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url="https://i.imgur.com/5fX8G0S.png")  # premium top-right

    await interaction.response.send_message(embed=embed, view=PanelButton(), ephemeral=True)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Command synced!")
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
