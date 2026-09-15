from src.entities.BaseCard import BaseCard

class SummonSlotCard(BaseCard):
    def __init__(self, x: float, y: float):
        # We pass the specific text and icon to the parent BaseCard
        super().__init__(x, y, "MoreSlot", "+ 1", "icon_XP_boost", "card_base_7")

    def apply_effect(self, player, play_state) -> None:
        """Adds an extra summon slot, capped at 3."""
        player.max_summons = min(3, player.max_summons + 1)
        # Remove this card from the pool if maxed out
        if player.max_summons == 3:
            if type(self) in play_state.card_manager.available_cards:
                play_state.card_manager.available_cards.remove(type(self))