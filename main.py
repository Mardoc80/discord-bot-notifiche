from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os

# Flask server per keep-alive (Render.com o Replit)
app = Flask('')

@app.route('/')
def home():
    return "Bot attivo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Intents necessari
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Il bot è online come {bot.user.name}")

@bot.event
async def on_presence_update(before, after):
    canale = discord.utils.get(after.guild.text_channels, name="notifiche-gioco")
    if after.activity and after.activity.type == discord.ActivityType.playing:
        if not before.activity or before.activity.name != after.activity.name:
            if canale:
                await canale.send(f"🎮 {after.name} ha iniziato a giocare a **{after.activity.name}**")
    elif before.activity and before.activity.type == discord.ActivityType.playing:
        if not after.activity or after.activity.type != discord.ActivityType.playing:
            if canale:
                await canale.send(f"🛑 {after.name} ha smesso di giocare a **{before.activity.name}**")

@bot.event
async def on_voice_state_update(member, before, after):
    canale = discord.utils.get(member.guild.text_channels, name="notifiche-vocale")
    if before.channel != after.channel:
        if canale:
            if after.channel and not before.channel:
                await canale.send(f"🎙️ {member.name} è entrato nel canale vocale **{after.channel.name}**")
            elif before.channel and not after.channel:
                await canale.send(f"📴 {member.name} è uscito dal canale vocale **{before.channel.name}**")
            elif before.channel != after.channel:
                await canale.send(f"🔄 {member.name} è passato da **{before.channel.name}** a **{after.channel.name}**")

# Avvio
keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
