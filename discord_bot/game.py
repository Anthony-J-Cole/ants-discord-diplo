import discord
from discord import app_commands
from discord.ext import commands

from ..game_manager import GameManager, GameManagerError
from ..order_parser import OrderParseError

class DiplomacyCog(commands.Cog):
    def __init__(self, bot: commands.Bot, game_manager: GameManager, default_map_path: str):
        self.bot = bot
        self.games = game_manager
        self.default_map_path = default_map_path

    group = app_commands.Group(name="ants-diplo-bot", description="")

    @group.command(name="create", description="start a game in the current channel")
    @app_commands.describe(name="Name of the game")
    async def create(self, interaction: discord.Interaction, name: str):
        game_id = self.games.create_game(name, self.default_map_path, channel_id=str(interaction.channel_id))
        await interaction.response.send_message(f"Created **{name}** (id `{game_id}`)\nPlayers: `/diplomacy join game_id:{game_id} power:<power>`")



    