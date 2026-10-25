"""Armazenamento SQLite compartilhado por todos os Cogs."""

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import aiosqlite

from config.classes import get_class


@dataclass(frozen=True)
class Character:
    user_id: int
    name: str
    class_key: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    xp: int
    level: int


class GameStore:
    """Salva personagens, itens e aventuras para o bot inteiro."""

    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self._write_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Cria o diretório e as tabelas necessárias na primeira execução."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS characters (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    class_key TEXT NOT NULL,
                    hp INTEGER NOT NULL,
                    max_hp INTEGER NOT NULL,
                    attack INTEGER NOT NULL,
                    defense INTEGER NOT NULL,
                    xp INTEGER NOT NULL DEFAULT 0,
                    level INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER NOT NULL REFERENCES characters(user_id) ON DELETE CASCADE,
                    item_key TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, item_key)
                );
                CREATE TABLE IF NOT EXISTS adventures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES characters(user_id) ON DELETE CASCADE,
                    action TEXT NOT NULL,
                    narrative TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            await db.commit()

    @staticmethod
    def _character(row: aiosqlite.Row | None) -> Character | None:
        if row is None:
            return None
        return Character(**dict(row))

    async def get_character(self, user_id: int) -> Character | None:
        async with aiosqlite.connect(self.database_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM characters WHERE user_id = ?", (user_id,))
            return self._character(await cursor.fetchone())

    async def create_character(self, character: Character, starter_items: dict[str, int]) -> bool:
        """Cria a ficha e os itens iniciais de forma conjunta."""
        async with self._write_lock, aiosqlite.connect(self.database_path) as db:
            try:
                await db.execute(
                    """INSERT INTO characters
                    (user_id, name, class_key, hp, max_hp, attack, defense, xp, level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        character.user_id, character.name, character.class_key,
                        character.hp, character.max_hp, character.attack,
                        character.defense, character.xp, character.level,
                    ),
                )
            except aiosqlite.IntegrityError:
                return False
            await db.executemany(
                "INSERT INTO inventory (user_id, item_key, quantity) VALUES (?, ?, ?)",
                [(character.user_id, item, quantity) for item, quantity in starter_items.items()],
            )
            await db.commit()
            return True

    async def set_hp(self, user_id: int, hp: int) -> Character | None:
        async with self._write_lock, aiosqlite.connect(self.database_path) as db:
            await db.execute("UPDATE characters SET hp = ? WHERE user_id = ?", (hp, user_id))
            await db.commit()
        return await self.get_character(user_id)

    async def take_damage(self, user_id: int, damage: int) -> Character | None:
        """Aplica dano sem permitir que a vida fique abaixo de zero."""
        async with self._write_lock, aiosqlite.connect(self.database_path) as db:
            await db.execute(
                "UPDATE characters SET hp = MAX(0, hp - ?) WHERE user_id = ?",
                (damage, user_id),
            )
            await db.commit()
        return await self.get_character(user_id)

    async def add_experience(self, user_id: int, amount: int) -> Character | None:
        """Adiciona XP e aplica os ganhos de atributo em Python ao subir de nível."""
        async with self._write_lock, aiosqlite.connect(self.database_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM characters WHERE user_id = ?", (user_id,))
            character = self._character(await cursor.fetchone())
            if character is None:
                return None

            total_xp = character.xp + amount
            new_level = total_xp // 100 + 1
            levels_gained = new_level - character.level
            class_rules = get_class(character.class_key)
            max_hp = character.max_hp + levels_gained * class_rules.hp_per_level
            await db.execute(
                """UPDATE characters SET xp = ?, level = ?, max_hp = ?,
                hp = CASE WHEN hp > 0 THEN hp + ? ELSE hp END,
                attack = attack + ?, defense = defense + ?
                WHERE user_id = ?""",
                (
                    total_xp, new_level, max_hp,
                    levels_gained * class_rules.hp_per_level,
                    levels_gained * class_rules.attack_per_level,
                    levels_gained * class_rules.defense_per_level,
                    user_id,
                ),
            )
            await db.commit()
        return await self.get_character(user_id)

    async def add_item(self, user_id: int, item_key: str, quantity: int = 1) -> None:
        async with self._write_lock, aiosqlite.connect(self.database_path) as db:
            await db.execute(
                """INSERT INTO inventory (user_id, item_key, quantity) VALUES (?, ?, ?)
                ON CONFLICT(user_id, item_key) DO UPDATE SET quantity = quantity + excluded.quantity""",
                (user_id, item_key, quantity),
            )
            await db.commit()

    async def consume_item(self, user_id: int, item_key: str) -> bool:
        """Remove uma unidade do inventário; retorna False se não houver estoque."""
        async with self._write_lock, aiosqlite.connect(self.database_path) as db:
            await db.execute("BEGIN IMMEDIATE")
            cursor = await db.execute(
                "SELECT quantity FROM inventory WHERE user_id = ? AND item_key = ?",
                (user_id, item_key),
            )
            row = await cursor.fetchone()
            if row is None or row[0] <= 0:
                await db.rollback()
                return False
            if row[0] == 1:
                await db.execute(
                    "DELETE FROM inventory WHERE user_id = ? AND item_key = ?",
                    (user_id, item_key),
                )
            else:
                await db.execute(
                    "UPDATE inventory SET quantity = quantity - 1 WHERE user_id = ? AND item_key = ?",
                    (user_id, item_key),
                )
            await db.commit()
            return True

    async def get_inventory(self, user_id: int) -> list[tuple[str, int]]:
        async with aiosqlite.connect(self.database_path) as db:
            cursor = await db.execute(
                "SELECT item_key, quantity FROM inventory WHERE user_id = ? AND quantity > 0 ORDER BY item_key",
                (user_id,),
            )
            return [(row[0], row[1]) for row in await cursor.fetchall()]

    async def record_adventure(self, user_id: int, action: str, narrative: str) -> None:
        async with self._write_lock, aiosqlite.connect(self.database_path) as db:
            await db.execute(
                "INSERT INTO adventures (user_id, action, narrative, created_at) VALUES (?, ?, ?, ?)",
                (user_id, action, narrative, datetime.now(UTC).isoformat()),
            )
            await db.commit()

    async def recent_adventures(self, user_id: int, limit: int = 3) -> list[tuple[str, str]]:
        async with aiosqlite.connect(self.database_path) as db:
            cursor = await db.execute(
                "SELECT action, narrative FROM adventures WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            )
            return [(row[0], row[1]) for row in reversed(await cursor.fetchall())]
