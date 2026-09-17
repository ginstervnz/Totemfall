from src.entities.BaseCard import BaseCard

class MoreMana(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Mana", "+15", "icon_mana_up", "card_base_5")

    def apply_effect(self, player, play_state) -> None:
        """Increases the maximum mana pool."""
        player.max_mana += 15.0
        player.mana += 15.0