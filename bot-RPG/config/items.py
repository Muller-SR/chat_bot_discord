"""Itens iniciais e seus efeitos definidos pelo código do jogo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    key: str
    name: str
    description: str
    effect: str
    value: int


ITEMS: dict[str, Item] = {
    "pocao": Item(
        key="pocao", name="Poção de cura", description="Recupera até 25 pontos de vida.",
        effect="healing", value=25,
    ),
    "pergaminho": Item(
        key="pergaminho", name="Pergaminho de experiência",
        description="Concede 25 pontos de experiência.", effect="experience", value=25,
    ),
}

STARTER_ITEMS = {"pocao": 2, "pergaminho": 1}
