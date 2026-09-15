from src.entities.BaseCard import BaseCard

class ManaReduce(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Less Cost", "- 1.5", "icon_mana_reduce", "card_base_4")

    def apply_effect(self, player, play_state) -> None:
        """Reduces the mana cost of shooting."""
        player.mana_cost = max(2.0, player.mana_cost - 1.5)