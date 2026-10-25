"""Classes de personagem e atributos iniciais do jogo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RPGClass:
    """Atributos iniciais e crescimento por nível de uma classe."""

    key: str
    name: str
    description: str
    max_hp: int
    attack: int
    defense: int
    hp_per_level: int = 8
    attack_per_level: int = 1
    defense_per_level: int = 1


CLASSES: dict[str, RPGClass] = {
    "guerreiro": RPGClass(
        key="guerreiro", name="Guerreiro", description="Resistente e forte no combate.",
        max_hp=120, attack=7, defense=6,
    ),
    "mago": RPGClass(
        key="mago", name="Mago", description="Poderoso, mas com pouca defesa.",
        max_hp=80, attack=10, defense=3,
    ),
    "arqueiro": RPGClass(
        key="arqueiro", name="Arqueiro", description="Ágil e equilibrado.",
        max_hp=95, attack=8, defense=4,
    ),
}


def get_class(class_key: str) -> RPGClass:
    """Retorna uma classe pelo nome usado internamente."""
    try:
        return CLASSES[class_key]
    except KeyError as error:
        raise ValueError("Classe desconhecida.") from error
