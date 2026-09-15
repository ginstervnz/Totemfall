from src.entities.BaseCard import BaseCard

class AllyDamageCard(BaseCard):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 'Summon', '+5 Dmg', 'icon_attack_damage','card_base')

    def apply_effect(self, player, play_state) -> None:
        """Increases the damage dealt by all future summoned melee allies."""
        player.ally_bonus_damage += 5