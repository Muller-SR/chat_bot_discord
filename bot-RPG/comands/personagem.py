"""Comandos para criar e consultar personagens."""

import discord
from discord import app_commands
from discord.ext import commands

from config.classes import CLASSES, get_class
from config.items import STARTER_ITEMS
from services.storage import Character


class PersonagemCog(commands.Cog):
    """Interface Discord para as fichas persistidas no GameStore."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="criar", description="Cria seu personagem de RPG.")
    @app_commands.describe(nome="Nome de 2 a 24 caracteres para seu personagem.", classe="Classe do personagem.")
    @app_commands.choices(
        classe=[
            app_commands.Choice(name=rules.name, value=key)
            for key, rules in CLASSES.items()
        ]
    )
    async def criar(
        self,
        interaction: discord.Interaction,
        nome: str,
        classe: app_commands.Choice[str],
    ) -> None:
        clean_name = " ".join(nome.split())
        if len(clean_name) < 2 or len(clean_name) > 24 or not clean_name.isprintable():
            await interaction.response.send_message(
                "O nome precisa ter de 2 a 24 caracteres visíveis.", ephemeral=True,
            )
            return

        rules = get_class(classe.value)
        character = Character(
            user_id=interaction.user.id,
            name=clean_name,
            class_key=rules.key,
            hp=rules.max_hp,
            max_hp=rules.max_hp,
            attack=rules.attack,
            defense=rules.defense,
            xp=0,
            level=1,
        )
        created = await self.bot.store.create_character(character, STARTER_ITEMS)
        if not created:
            await interaction.response.send_message(
                "Você já tem um personagem. Use `/ficha` para consultar sua ficha.", ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"Personagem criado: {character.name}",
            description=f"{rules.name} — {rules.description}",
            color=discord.Color.dark_gold(),
        )
        embed.add_field(name="Vida", value=f"{character.hp}/{character.max_hp}")
        embed.add_field(name="Ataque", value=str(character.attack))
        embed.add_field(name="Defesa", value=str(character.defense))
        embed.set_footer(text="Você também recebeu 2 poções e 1 pergaminho de experiência.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ficha", description="Mostra os dados do seu personagem.")
    async def ficha(self, interaction: discord.Interaction) -> None:
        character = await self.bot.store.get_character(interaction.user.id)
        if character is None:
            await interaction.response.send_message(
                "Você ainda não criou um personagem. Use `/criar`.", ephemeral=True,
            )
            return

        rules = get_class(character.class_key)
        embed = discord.Embed(
            title=character.name,
            description=f"{rules.name} — nível {character.level}",
            color=discord.Color.dark_gold(),
        )
        embed.add_field(name="Vida", value=f"{character.hp}/{character.max_hp}", inline=True)
        embed.add_field(name="Ataque", value=str(character.attack), inline=True)
        embed.add_field(name="Defesa", value=str(character.defense), inline=True)
        embed.add_field(name="Experiência", value=f"{character.xp} / {character.level * 100} XP", inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PersonagemCog(bot))
