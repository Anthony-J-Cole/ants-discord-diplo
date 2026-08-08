# TODO: Run in docker container

import logging
import os

import discord
from discord.ext import commands

from .db import Storage
from .game_manager import GameManager
from .cogs.game import DiplomacyCog

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("diplo-bot")

# Set via environment var or default
DB_PATH = os.environ.get("DB_PATH", "/data/diplomacy.db")
DEFAULT_MAP_PATH = os.environ.get("DEFAULT_MAP_PATH", "/ants-discord-diplo/maps/test_map.json")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        log.info(f"Synced {len(synced)} slash commands")
    except Exception:
        log.exception("Slash commands failed")

async def _setup():
    storage = Storage(DB_PATH)
    game_manager = GameManager(storage)
    await bot.add_cog(DiplomacyCog(bot, game_manager, DEFAULT_MAP_PATH))

def main():
    token = os.environ["DISCORD_TOKEN"]
    bot.setup_hook = _setup
    bot.run(token)

if __name__ == "__main__":
    main()