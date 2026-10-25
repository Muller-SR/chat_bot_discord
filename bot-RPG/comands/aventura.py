"""Aventura interativa com narração por IA ou demonstração local."""

import discord
from discord import app_commands
from discord.ext import commands

from services.narrator import Narrator


class AventuraCog(commands.Cog):
    """Coordena narrativa e histórico sem delegar regras à IA."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="aventura", description="Continua a aventura do seu personagem.")
    @app_commands.describe(acao="Descreva o que seu personagem tenta fazer (até 300 caracteres).")
    async def aventura(self, interaction: discord.Interaction, acao: str) -> None:
        action = acao.strip()
        if not action or len(action) > 300:
            await interaction.response.send_message(
                "Descreva uma ação com até 300 caracteres.", ephemeral=True,
            )
            return

        character = await self.bot.store.get_character(interaction.user.id)
        if character is None:
            await interaction.response.send_message(
                "Crie um personagem primeiro com `/criar`.", ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)
        history = await self.bot.store.recent_adventures(interaction.user.id)
        narrator = Narrator(self.bot.settings)
        try:
            narrative, mode = await narrator.narrate(character, action, history)
            status = "Modo de demonstração" if mode == "demo" else f"Narrado com {mode.title()}"
        except Exception:
            # Um erro temporário na API não impede a oficina de continuar.
            narrative = narrator._demo_story(character, action)
            status = "Modo de demonstração (serviço de IA indisponível)"

        narrative = narrative[:4000]
        updated_character = await self.bot.store.add_experience(interaction.user.id, 10)
        await self.bot.store.record_adventure(interaction.user.id, action, narrative)

        embed = discord.Embed(
            title=f"Aventura de {character.name}",
            description=narrative,
            color=discord.Color.dark_purple(),
        )
        if updated_character:
            embed.set_footer(
                text=f"{status} • +10 XP • Nível {updated_character.level} • "
                f"Vida {updated_character.hp}/{updated_character.max_hp}"
            )
        await interaction.edit_original_response(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AventuraCog(bot))
