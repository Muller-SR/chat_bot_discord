"""Combate entre personagens com rolagens e cálculos feitos em Python."""

import random

import discord
from discord import app_commands
from discord.ext import commands


class CombateCog(commands.Cog):
    """Executa ataques e grava o dano no armazenamento compartilhado."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="atacar", description="Ataca o personagem de outro participante.")
    @app_commands.guild_only()
    async def atacar(self, interaction: discord.Interaction, alvo: discord.Member) -> None:
        if alvo.id == interaction.user.id:
            await interaction.response.send_message("Você não pode atacar a si mesmo.", ephemeral=True)
            return

        attacker = await self.bot.store.get_character(interaction.user.id)
        defender = await self.bot.store.get_character(alvo.id)
        if attacker is None or defender is None:
            await interaction.response.send_message(
                "Você e o alvo precisam ter personagens criados com `/criar`.", ephemeral=True,
            )
            return
        if attacker.hp <= 0:
            await interaction.response.send_message(
                "Seu personagem está sem vida. Use uma poção antes de lutar.", ephemeral=True,
            )
            return
        if defender.hp <= 0:
            await interaction.response.send_message(f"{defender.name} já está sem vida.", ephemeral=True)
            return

        attack_roll = random.randint(1, 20)
        target_number = 10 + defender.defense
        total = attack_roll + attacker.attack
        hit = total >= target_number
        damage = max(1, random.randint(1, 6) + attacker.attack - defender.defense // 2) if hit else 0

        updated_defender = await self.bot.store.take_damage(alvo.id, damage) if hit else defender
        knocked_out = bool(updated_defender and updated_defender.hp == 0)
        updated_attacker = attacker
        if knocked_out:
            updated_attacker = await self.bot.store.add_experience(interaction.user.id, 20) or attacker

        embed = discord.Embed(
            title="Ataque acertou!" if hit else "Ataque errou",
            description=(
                f"{attacker.name} rolou **{attack_roll}** + ataque **{attacker.attack}** = **{total}**.\n"
                f"Alvo precisava de **{target_number}**."
            ),
            color=discord.Color.red() if hit else discord.Color.dark_grey(),
        )
        if hit and updated_defender:
            embed.add_field(
                name="Dano",
                value=f"{damage} — {updated_defender.name}: "
                f"{updated_defender.hp}/{updated_defender.max_hp} vida",
                inline=False,
            )
        if knocked_out:
            embed.add_field(name="Nocaute", value=f"{attacker.name} ganhou 20 XP.", inline=False)
        if updated_attacker.level > attacker.level:
            embed.set_footer(text=f"{attacker.name} subiu para o nível {updated_attacker.level}!")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CombateCog(bot))
