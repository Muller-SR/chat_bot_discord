"""Comando para rolar os dados usados na oficina de RPG."""

import random

import discord
from discord import app_commands
from discord.ext import commands


class DadosCog(commands.Cog):
    """Rola D6, D10, D12 ou D20 usando a biblioteca padrão random."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="dado", description="Rola um dado de RPG.")
    @app_commands.choices(
        faces=[
            app_commands.Choice(name=f"D{number}", value=number)
            for number in (6, 10, 12, 20)
        ]
    )
    async def dado(self, interaction: discord.Interaction, faces: app_commands.Choice[int]) -> None:
        result = random.randint(1, faces.value)
        embed = discord.Embed(
            title=f"Rolagem de D{faces.value}",
            description=f"{interaction.user.mention} tirou **{result}**.",
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DadosCog(bot))
