import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from motor.motor_asyncio import AsyncIOMotorClient

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "dedpost")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

mongo = AsyncIOMotorClient(MONGO_URI)
db = mongo[DB_NAME]
settings_db = db.settings


# -----------------------------
# HELPERS
# -----------------------------
async def get_settings(guild_id: int):
    data = await settings_db.find_one({"guild_id": guild_id})
    if not data:
        default = {
            "guild_id": guild_id,
            "token": None,
            "message": None,
            "channel_id": None,
            "delay": 10,
            "webhook": None,
            "active": False
        }
        await settings_db.insert_one(default)
        return default
    return data


# -----------------------------
# MODAL FORM PREMIUM
# -----------------------------
class AccountModal(discord.ui.Modal, title="✨ Account Management (Premium)"):
    token = discord.ui.TextInput(
        label="🔑 Token",
        placeholder="Masukkan token Anda...",
        required=True
    )
    message = discord.ui.TextInput(
        label="💬 Message",
        placeholder="Tulis message untuk autopost...",
        style=discord.TextStyle.long,
        required=True,
        max_length=3900
    )
    channel = discord.ui.TextInput(
        label="📺 Channel ID",
        placeholder="Contoh: 123456789012345678",
        required=True
    )
    delay = discord.ui.TextInput(
        label="⏱ Delay (Minutes)",
        placeholder="Contoh: 10",
        required=True
    )
    webhook = discord.ui.TextInput(
        label="🔗 Webhook URL (Optional)",
        placeholder="Isi jika pakai webhook",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        await settings_db.update_one(
            {"guild_id": guild_id},
            {"$set": {
                "token": self.token.value,
                "message": self.message.value,
                "channel_id": self.channel.value,
                "delay": int(self.delay.value),
                "webhook": self.webhook.value
            }},
            upsert=True
        )
        await interaction.response.send_message("✅ **Settings updated successfully!**", ephemeral=True)


# -----------------------------
# BUTTON UI
# -----------------------------
class PanelButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔧 Manage Account", style=discord.ButtonStyle.blurple)
    async def manage(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AccountModal())

    @discord.ui.button(label="📊 Account Info", style=discord.ButtonStyle.gray)
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await get_settings(interaction.guild.id)

        embed = discord.Embed(
            title="📊 AUTOPOST ACCOUNT INFO",
            color=0x3498db
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")
        embed.add_field(name="🔑 Token", value=f"```{data.get('token','None')}```", inline=False)
        embed.add_field(name="💬 Message", value=f"```{data.get('message','None')}```", inline=False)
        embed.add_field(name="📺 Channel ID", value=data.get("channel_id","None"), inline=False)
        embed.add_field(name="⏱ Delay", value=f"{data.get('delay')} minutes", inline=False)
        embed.add_field(name="🔗 Webhook", value=data.get("webhook","None"), inline=False)
        embed.add_field(name="🚀 Status", value="Active ✅" if data.get("active") else "Inactive ❌", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🚀 Start / Stop Autopost", style=discord.ButtonStyle.green)
    async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await get_settings(interaction.guild.id)
        new_state = not data.get("active")
        await settings_db.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"active": new_state}}
        )
        await interaction.response.send_message(
            f"🚀 Autopost set to: **{new_state}**",
            ephemeral=True
        )

    @discord.ui.button(label="🌐 Create Webhook", style=discord.ButtonStyle.grey)
    async def create_webhook(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        webhook = await channel.create_webhook(name="DedAutoPost Webhook")
        await settings_db.update_one({"guild_id": interaction.guild.id}, {"$set": {"webhook": webhook.url}})
        await interaction.response.send_message(f"🔗 Webhook created:\n{webhook.url}", ephemeral=True)



# -----------------------------
# PANEL COMMAND
# -----------------------------
@bot.tree.command(name="panel", description="Open the Autopost Control Panel")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💎 PREMIUM AUTOPOST PANEL",
        description="Manage your autopost settings using the buttons below.",
        color=0x5dade2
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/1.png")

    await interaction.response.send_message(embed=embed, view=PanelButtons(), ephemeral=True)


# -----------------------------
# READY EVENT
# -----------------------------
@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print("Commands synced:", len(synced))
    except Exception as e:
        print("ERROR:", e)


# -----------------------------
# RUN BOT
# -----------------------------
bot.run(DISCORD_TOKEN)
