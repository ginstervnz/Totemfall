from src.entities.BaseCard import BaseCard

class SpeedUpCard(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Spd Up", "+10 spd", "icon_speed_up", "card_base_2")

    def apply_effect(self, player, play_state) -> None:
        """Increases movement speed."""
        player.speed += 10