from src.entities.BaseCard import BaseCard

class ShootSpeed(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Shot", "+20 Spd", "icon_shoot_speed", "card_base_5")

    def apply_effect(self, player, play_state) -> None:
        """Increases the travel speed of the magic bolts."""
        player.projectile_config['speed'] += 20