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
            await canale_vocale.send(f"🎙️ {member.name} è **entrato** nel canale vocale **{after.channel.name}**")
        elif before.channel is not None and after.channel is None:
            await canale_vocale.send(f"🔕 {member.name} è **uscito** dal canale vocale **{before.channel.name}**")
        elif before.channel != after.channel:
            await canale_vocale.send(f"🔄 {member.name} è passato da **{before.channel.name}** a **{after.channel.name}**")

@bot.event
async def on_presence_update(before, after):
    canale_gioco = discord.utils.get(after.guild.text_channels, name="notifiche-gioco")
    if not canale_gioco:
        print(f"⚠️ Canale 'notifiche-gioco' non trovato nella guild {after.guild.name}")
        return

    # Quando inizia a giocare a qualcosa di nuovo
    if after.activity and after.activity.type == discord.ActivityType.playing:
        # Se prima non giocava o gioco cambiato
        if not before.activity or before.activity.name != after.activity.name:
            await canale_gioco.send(f"🎮 {after.name} ha iniziato a giocare a **{after.activity.name}**")

    # Quando smette di giocare
    elif before.activity and before.activity.type == discord.ActivityType.playing:
        if not after.activity or after.activity.type != discord.ActivityType.playing:
            await canale_gioco.send(f"🛑 {after.name} ha smesso di giocare a **{before.activity.name}**")

# Avvio
keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
