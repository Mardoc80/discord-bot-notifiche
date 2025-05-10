from flask import Flask
from threading import Thread
import discord
from discord.ext import commands, tasks
import os
import json
from datetime import datetime

# Keep-alive per render.com / Replit
app = Flask('')

@app.route('/')
def home():
    return "Bot online!"

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

# Variabili globali per tracciare il tempo di gioco
sessioni_attive = {}  # Salva {utente_id: timestamp_inizio}

# Caricamento dati
def carica_dati(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r") as f:
            return json.load(f)
    return {}

dati_globali = carica_dati("data.json")
dati_mensili = carica_dati("data_mensile.json")

def salva_dati():
    with open("data.json", "w") as f:
        json.dump(dati_globali, f)
    with open("data_mensile.json", "w") as f:
        json.dump(dati_mensili, f)

@bot.event
async def on_ready():
    print(f"✅ Il bot è online come {bot.user.name}")
    invia_classifica_mensile.start()

@bot.event
async def on_presence_update(before, after):
    canale = discord.utils.get(after.guild.text_channels, name="notifiche-gioco")
    ora = datetime.utcnow()

    # Inizia a giocare
    if after.activity and after.activity.type == discord.ActivityType.playing:
        if not before.activity or before.activity.name != after.activity.name:
            if canale:
                await canale.send(f"🎮 {after.name} ha iniziato a giocare a **{after.activity.name}**")
            sessioni_attive[after.id] = ora

    # Smette di giocare
    if before.activity and before.activity.type == discord.ActivityType.playing:
        if not after.activity or after.activity.type != discord.ActivityType.playing:
            inizio = sessioni_attive.pop(after.id, None)
            if inizio:
                durata = int((ora - inizio).total_seconds())
                dati_globali[after.name] = dati_globali.get(after.name, 0) + durata
                dati_mensili[after.name] = dati_mensili.get(after.name, 0) + durata
                salva_dati()

            if canale:
                await canale.send(f"🛑 {after.name} ha smesso di giocare a **{before.activity.name}**")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        canale_vocale = discord.utils.get(member.guild.text_channels, name="notifiche-vocale")
        if canale_vocale and after.channel:
            await canale_vocale.send(f"🎙️ {member.name} è entrato nel canale vocale **{after.channel.name}**")

@bot.command()
async def classifica(ctx):
    if ctx.channel.name != "classifica-giocatori":
        await ctx.send("❌ Questo comando può essere usato solo nel canale #classifica-giocatori.")
        return

    if not dati_globali:
        await ctx.send("📭 Nessun dato disponibile.")
        return

    classifica = sorted(dati_globali.items(), key=lambda x: x[1], reverse=True)
    messaggio = "**🏆 Classifica globale dei giocatori:**\n"
    for i, (utente, secondi) in enumerate(classifica, start=1):
        ore = round(secondi / 3600, 2)
        messaggio += f"{i}. {utente}: {ore} ore\n"

    await ctx.send(messaggio)

@bot.command()
async def classifica_mese(ctx):
    if ctx.channel.name != "classifica-giocatori":
        await ctx.send("❌ Questo comando può essere usato solo nel canale #classifica-giocatori.")
        return

    if not dati_mensili:
        await ctx.send("📭 Nessun dato mensile disponibile.")
        return

    classifica = sorted(dati_mensili.items(), key=lambda x: x[1], reverse=True)
    messaggio = "**📅 Classifica mensile dei giocatori:**\n"
    for i, (utente, secondi) in enumerate(classifica, start=1):
        ore = round(secondi / 3600, 2)
        messaggio += f"{i}. {utente}: {ore} ore\n"

    await ctx.send(messaggio)

@tasks.loop(hours=24)
async def invia_classifica_mensile():
    oggi = datetime.now()
    if oggi.day == 30:
        for guild in bot.guilds:
            canale = discord.utils.get(guild.text_channels, name="classifica-giocatori")
            if canale:
                await canale.send("📅 Fine mese! Ecco le classifiche aggiornate:\n")

                await canale.send("**📅 Classifica mensile:**")
                if dati_mensili:
                    classifica_m = sorted(dati_mensili.items(), key=lambda x: x[1], reverse=True)
                    messaggio_m = ""
                    for i, (utente, secondi) in enumerate(classifica_m, start=1):
                        ore = round(secondi / 3600, 2)
                        messaggio_m += f"{i}. {utente}: {ore} ore\n"
                    await canale.send(messaggio_m)
                else:
                    await canale.send("Nessun dato disponibile per il mese.")

                await canale.send("**🏆 Classifica globale:**")
                if dati_globali:
                    classifica_g = sorted(dati_globali.items(), key=lambda x: x[1], reverse=True)
                    messaggio_g = ""
                    for i, (utente, secondi) in enumerate(classifica_g, start=1):
                        ore = round(secondi / 3600, 2)
                        messaggio_g += f"{i}. {utente}: {ore} ore\n"
                    await canale.send(messaggio_g)
                else:
                    await canale.send("Nessun dato globale disponibile.")

        dati_mensili.clear()
        salva_dati()

# Avvio
keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
