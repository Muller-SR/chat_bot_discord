"""Ponto de entrada do bot Mestre RPG."""

import asyncio
import logging
import pkgutil

import discord
import comands
from discord.ext import commands

from config.settings import Settings, load_settings
from services.storage import GameStore


class MestreRPGBot(commands.Bot):
    """Bot que carrega os Cogs e publica comandos no servidor de testes."""

    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.settings = settings
        self.store = GameStore(settings.database_path)

    async def setup_hook(self) -> None:
        """Carrega as extensões antes de sincronizar os slash commands."""
        await self.store.initialize()

        # Cada módulo Python dentro de comands/ pode registrar um ou mais Cogs.
        for module in pkgutil.iter_modules(comands.__path__, f"{comands.__name__}."):
            await self.load_extension(module.name)

        test_guild = discord.Object(id=self.settings.discord_guild_id)
        self.tree.copy_global_to(guild=test_guild)
        synced_commands = await self.tree.sync(guild=test_guild)
        logging.info("%s comando(s) sincronizado(s) no servidor de testes.", len(synced_commands))


def create_bot(settings: Settings) -> MestreRPGBot:
    """Cria o bot separadamente para deixar a inicialização fácil de acompanhar."""
    return MestreRPGBot(settings)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    bot = create_bot(settings)

    # start() abre a conexão e mantém o programa rodando até o bot ser desligado.
    async with bot:
        await bot.start(settings.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
