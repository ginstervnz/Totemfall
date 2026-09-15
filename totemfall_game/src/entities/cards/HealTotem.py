from src.entities.BaseCard import BaseCard

class HealTotem(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Heal", "2 hits", "icon_heal_totem", "card_base_6")

    def apply_effect(self, player, play_state) -> None:
        """Restores a bit of its HP."""
        play_state.totem.hp += 2