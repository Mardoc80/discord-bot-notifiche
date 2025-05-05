from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

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
    if before.activity and before.activity.type == discord.ActivityType.playing:
        if not after.activity or after.activity.type != discord.ActivityType.playing:
            if canale:
                await canale.send(f"🛑 {after.name} ha smesso di giocare a **{before.activity.name}**")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        canale = discord.utils.get(member.guild.text_channels, name="notifiche-gioco")
        if canale:
            await canale.send(f"🎙️ {member.name} è entrato nel canale vocale **{after.channel.name}**")

keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
