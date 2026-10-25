"""Cog pequeno para confirmar que o bot está respondendo."""

import discord
from discord import app_commands
from discord.ext import commands


class PingCog(commands.Cog):
    """Agrupa o comando de teste /ping."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Verifica se o bot está online.")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Responde com a latência atual do bot em milissegundos."""
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latência: {latency_ms} ms.")


async def setup(bot: commands.Bot) -> None:
    """Ponto de entrada chamado por bot.load_extension()."""
    await bot.add_cog(PingCog(bot))
