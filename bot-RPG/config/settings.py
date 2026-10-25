"""Leitura e validação das configurações externas do projeto."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Configurações usadas pelo Discord, pelos provedores de IA e pelo banco."""

    discord_token: str
    discord_guild_id: int
    openai_api_key: str | None
    openai_model: str
    gemini_api_key: str | None
    gemini_model: str
    ai_provider: str
    database_path: str


def load_settings() -> Settings:
    """Carrega .env e valida as opções necessárias para iniciar o bot."""
    load_dotenv()

    discord_token = os.getenv("DISCORD_TOKEN", "").strip()
    if not discord_token:
        raise ValueError("Defina DISCORD_TOKEN no arquivo .env.")

    guild_id_value = os.getenv("DISCORD_GUILD_ID", "").strip()
    if not guild_id_value:
        raise ValueError("Defina DISCORD_GUILD_ID no arquivo .env.")
    try:
        discord_guild_id = int(guild_id_value)
    except ValueError as error:
        raise ValueError("DISCORD_GUILD_ID precisa ser um número inteiro.") from error
    if discord_guild_id <= 0:
        raise ValueError("DISCORD_GUILD_ID precisa ser maior que zero.")

    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip() or None
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    ai_provider = os.getenv("AI_PROVIDER", "auto").strip().lower()
    if ai_provider not in {"auto", "demo", "openai", "gemini"}:
        raise ValueError("AI_PROVIDER deve ser auto, demo, openai ou gemini.")
    if ai_provider == "openai" and not openai_api_key:
        raise ValueError("AI_PROVIDER=openai requer OPENAI_API_KEY.")
    if ai_provider == "gemini" and not gemini_api_key:
        raise ValueError("AI_PROVIDER=gemini requer GEMINI_API_KEY.")
    if not openai_model or not gemini_model:
        raise ValueError("Os nomes dos modelos de IA não podem ficar vazios.")
    database_path = os.getenv("DATABASE_PATH", "data/mestre_rpg.sqlite3").strip()
    if not database_path:
        raise ValueError("DATABASE_PATH não pode ficar vazio.")

    return Settings(
        discord_token=discord_token,
        discord_guild_id=discord_guild_id,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
        ai_provider=ai_provider,
        database_path=database_path,
    )
