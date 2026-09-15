from src.entities.BaseCard import BaseCard

class XPBoost(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "XP", "FREE!", "icon_XP_boost", "card_base_4")

    def apply_effect(self, player, play_state) -> None:
        """Grants a massive chunk of XP instantly (50% of the current requirement)."""
        bonus_xp = int(player.xp_to_next_level * 0.5) 
        player.add_xp(bonus_xp)