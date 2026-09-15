from src.entities.BaseCard import BaseCard

class DamageCard(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Atk Up", "+5 Dmg", "icon_attack_damage", "card_base")

    def apply_effect(self, player, play_state) -> None:
        """Increases the global damage in the PlayState."""
        play_state.player_damage += 5