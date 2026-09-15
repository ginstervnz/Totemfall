from src.entities.BaseCard import BaseCard

class SummonUnlockCard(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "Summon", "+ 1", "icon_shoot_speed", "card_base_7")

    def apply_effect(self, player, play_state) -> None:
        """Unlocks the first summon slot and updates the card pool."""
        player.max_summons = 1
        play_state.card_manager.unlock_summon_upgrades()