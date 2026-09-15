from src.entities.BaseCard import BaseCard

class ManaUP(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Mana", "+ RG", "icon_regeneration_mana", "card_base_4")

    def apply_effect(self, player, play_state) -> None:
        """Increases passive mana regeneration."""
        player.mana_regen += 5.0