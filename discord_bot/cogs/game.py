import discord
from discord import app_commands
from discord.ext import commands

from ..game_manager import GameManager, GameManagerError
from ..order_parser import OrderParseError
from ..map_renderer import render_png

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

    @group.command(name="join", description="Join a game in progress")
    async def join(self, interaction: discord.Interaction, game_id: str, power:str):
        try: 
            self.games.join(game_id, power.lower, str(interaction.user.id))
            await interaction.response.send_message(f"{interaction.user.mention} is now playing as {power}", ephemeral=False)
        except GameManagerError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

    @group.command(name="order", description="Submit an order")
    async def order(self, interaction: discord.Interaction, game_id: str, order_text: str):
        try:
            msg = self.games.submit_order(game_id, str(interaction.user.id), order_text)
            await interaction.response.send_message(msg, ephemeral=True)
        except (GameManagerError, OrderParseError) as e:
            await interaction.response.send_message(f"Cant submit that order: {e}", ephemeral=True)

        @group.command(name="orders", description="Show your currently submitted orders")
    async def orders(self, interaction: discord.Interaction, game_id: str):
        try:
            mine = self.games.my_orders(game_id, str(interaction.user.id))
            text = "\n".join(mine) if mine else "No orders submitted yet."
            await interaction.response.send_message(text, ephemeral=True)
        except GameManagerError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
 
    @group.command(name="process", description="Process the turn")
     @app_commands.checks.has_permissions(manage_guild=True)
    async def process(self, interaction: discord.Interaction, game_id: str):
        new_state = self.games.process_phase(game_id)
        game_map = self.games.get_map(game_id)
        content = f"Phase resolved. Now: **{new_state.year} {new_state.season} {new_state.phase.value}**"
        try:
            png_bytes = render_png(game_map, new_state)
            file = discord.File(io.BytesIO(png_bytes), filename="map.png")
            await interaction.response.send_message(content=content, file=file)
        except ValueError:
            await interaction.response.send_message(content)
    
        @group.command(name="map", description="Show the current board")
    async def map_(self, interaction: discord.Interaction, game_id: str):
        state = self.games.get_state(game_id)
        game_map = self.games.get_map(game_id)
        try:
            png_bytes = render_png(game_map, state)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        file = discord.File(io.BytesIO(png_bytes), filename="map.png")
        await interaction.response.send_message(
            content=f"**{state.year} {state.season} {state.phase.value}**", file=file
        )


    async def setup(bot: commands.bot):
        pass

    