from src.entities.BaseCard import BaseCard

class TotemShieldCard(BaseCard):
    def __init__(self, x: float, y: float):
        # We reuse the blocks icon or any other suitable icon you have
        super().__init__(x, y, "Aegis", "Immunity", "icon_blocks", "card_base_3")

    def apply_effect(self, player, play_state) -> None:
        """Grants the Totem a temporary procedural shield every 12 seconds."""
        play_state.totem.has_shield_ability = True
        play_state.totem.shield_cooldown_max = 12.0
        play_state.totem.shield_duration_max = 2.5
        play_state.totem.reset_shield()
        
        # Remove this card from the pool so it only appears once
        play_state.card_manager.remove_card(self.__class__)
        