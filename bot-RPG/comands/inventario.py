"""Consulta inventário e usa itens com efeitos controlados pelo código."""

import discord
from discord import app_commands
from discord.ext import commands

from config.items import ITEMS


class InventarioCog(commands.Cog):
    """Aplica os efeitos de poções e pergaminhos em Python."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="inventario", description="Mostra os itens do seu personagem.")
    async def inventario(self, interaction: discord.Interaction) -> None:
        character = await self.bot.store.get_character(interaction.user.id)
        if character is None:
            await interaction.response.send_message("Crie um personagem primeiro com `/criar`.", ephemeral=True)
            return

        inventory = await self.bot.store.get_inventory(interaction.user.id)
        embed = discord.Embed(title=f"Inventário de {character.name}", color=discord.Color.dark_green())
        if not inventory:
            embed.description = "Seu inventário está vazio."
        else:
            embed.description = "\n".join(
                f"**{ITEMS[item_key].name}** × {quantity} — {ITEMS[item_key].description}"
                for item_key, quantity in inventory if item_key in ITEMS
            ) or "Seu inventário está vazio."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="usar", description="Usa uma poção ou pergaminho do inventário.")
    @app_commands.choices(
        item=[app_commands.Choice(name=definition.name, value=key) for key, definition in ITEMS.items()]
    )
    async def usar(self, interaction: discord.Interaction, item: app_commands.Choice[str]) -> None:
        character = await self.bot.store.get_character(interaction.user.id)
        if character is None:
            await interaction.response.send_message("Crie um personagem primeiro com `/criar`.", ephemeral=True)
            return

        definition = ITEMS[item.value]
        if definition.effect == "healing" and character.hp >= character.max_hp:
            await interaction.response.send_message("Sua vida já está cheia.", ephemeral=True)
            return
        if not await self.bot.store.consume_item(interaction.user.id, item.value):
            await interaction.response.send_message("Você não tem esse item no inventário.", ephemeral=True)
            return

        if definition.effect == "healing":
            new_hp = min(character.max_hp, max(1, character.hp) + definition.value)
            updated = await self.bot.store.set_hp(interaction.user.id, new_hp)
            recovered = new_hp - character.hp
            description = f"{character.name} recuperou {recovered} pontos de vida."
            if character.hp == 0:
                description = f"{character.name} voltou ao combate com {new_hp} pontos de vida."
        else:
            updated = await self.bot.store.add_experience(interaction.user.id, definition.value)
            description = f"{character.name} recebeu {definition.value} XP."

        embed = discord.Embed(title=definition.name, description=description, color=discord.Color.green())
        if updated:
            embed.add_field(name="Vida", value=f"{updated.hp}/{updated.max_hp}", inline=True)
            embed.add_field(name="Nível", value=str(updated.level), inline=True)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InventarioCog(bot))
