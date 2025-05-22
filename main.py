from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os

# Keep-alive per Render.com
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot attivo."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Intents
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Il bot è online come {bot.user.name}")

@bot.event
async def on_voice_state_update(member, before, after):
    canale_vocale = discord.utils.get(member.guild.text_channels, name="notifiche-vocale")

    if canale_vocale:
        if before.channel is None and after.channel is not None:
            # Entrata in un canale vocale
            await canale_vocale.send(f"🎙️ {member.name} è **entrato** nel canale vocale **{after.channel.name}**")
        elif before.channel is not None and after.channel is None:
            # Uscita da un canale vocale
            await canale_vocale.send(f"🔕 {member.name} è **uscito** dal canale vocale **{before.channel.name}**")
        elif before.channel != after.channel:
            # Cambio di canale vocale
            await canale_vocale.send(f"🔄 {member.name} è passato da **{before.channel.name}** a **{after.channel.name}**")

# Avvio
keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
