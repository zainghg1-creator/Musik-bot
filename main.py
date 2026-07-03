import sys
from types import ModuleType

# Wichtig für die Python 3.13 Serverumgebung auf Render
if 'audioop' not in sys.modules:
    sys.modules['audioop'] = ModuleType('audioop')

import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# ====================================================================
# TRAG HIER DEINE ECHTEN IDS EIN:
# ====================================================================
KANAL_ID = 123456789012345678       # ID deines Log-Kanals auf Discord

intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Wichtig, damit der Bot die Rollen der Mitglieder sehen und bearbeiten darf

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Der Bot ist eingeloggt als: {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"Erfolgreich {len(synced)} Slash-Command(s) auf Render synchronisiert!")
    except Exception as e:
        print(f"Fehler beim Synchronisieren: {e}")

# --- TIMEOUT-HELFER: Entfernt die Rolle automatisch nach Ablauf der Zeit ---
async def entferne_rolle_nach_zeit(member, rolle, tage):
    sekunden = tage * 24 * 60 * 60
    await asyncio.sleep(sekunden)
    
    if member and rolle in member.roles:
        try:
            await member.remove_roles(rolle)
            print(f"Zeit abgelaufen: {rolle.name} wurde von {member.name} entfernt.")
        except Exception as e:
            print(f"Fehler beim automatischen Entfernen der Rolle: {e}")

# --- SLASH-COMMANDS ---

@bot.tree.command(name="ping", description="Antwortet mit Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

# DER WARN-BEFEHL (Mit deinen exakten Rollen-Namen)
@bot.tree.command(name="teamwarn", description="Erstellt eine Warnung, ermittelt die nächste Stufe & vergibt die Rolle")
@app_commands.describe(
    wer="Welches Teammitglied wird gewarnt?", 
    grund="Was hat das Mitglied getan?", 
    dauer="Anzahl der Tage (nur Zahlen!)", 
    unterschrift="Wer unterschreibt?"
)
async def teamwarn(interaction: discord.Interaction, wer: discord.Member, grund: str, dauer: int, unterschrift: discord.Member):
    await interaction.response.defer(ephemeral=True)
    
    # Deine exakten Rollen-Namen vom Server
    warn_rollen_namen = ["⚠️《 | Temp Warn 1", "⚠️《 | Temp Warn 2", "⚠️《 | Temp Warn 3"]
    aktuelle_stufe = 0
    neue_rolle_name = "⚠️《 | Temp Warn 1"
    
    # 1. Prüfen, welche Warnung das Mitglied aktuell schon aktiv hat
    for rolle in wer.roles:
        if rolle.name in warn_rollen_namen:
            if rolle.name == "⚠️《 | Temp Warn 1":
                aktuelle_stufe = 1
                neue_rolle_name = "⚠️《 | Temp Warn 2"
            elif rolle.name == "⚠️《 | Temp Warn 2":
                aktuelle_stufe = 2
                neue_rolle_name = "⚠️《 | Temp Warn 3"
            elif rolle.name == "⚠️《 | Temp Warn 3":
                aktuelle_stufe = 3
                neue_rolle_name = "⚠️《 | Temp Warn 3"
                
    guild = interaction.guild
    neue_rolle = discord.utils.get(guild.roles, name=neue_rolle_name)
    
    if not neue_rolle:
        await interaction.followup.send(f"❌ Fehler: Die Rolle `{neue_rolle_name}` wurde auf diesem Server nicht gefunden! Prüfe die Schreibweise.", ephemeral=True)
        return
        
    try:
        # 2. Dem User die neue Rolle geben
