from src.entities.BaseCard import BaseCard

class LightningDamageCard(BaseCard):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "VoltDmg", "+3 Dmg", "icon_attack_damage", "card_base_4")

    def apply_effect(self, player, play_state) -> None:
        """Increases the damage of the chain lightning arcs."""
        if hasattr(player, 'lightning_damage'):
            player.lightning_damage += 3.0
            
