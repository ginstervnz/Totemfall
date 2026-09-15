from src.entities.BaseCard import BaseCard

class AtkSpeedUP(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Spd Atk", "+ FR", "icon_atk_speed_up", "card_base_3")

    def apply_effect(self, player, play_state) -> None:
        """Reduces the time between shots."""
        player.fire_rate = max(0.1, player.fire_rate - 0.05)