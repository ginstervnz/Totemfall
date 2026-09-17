from src.entities.BaseCard import BaseCard
import random

class LightningUnlockCard(BaseCard):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Chain Volt", "Unlock", "icon_mana_up", "card_base")

    def apply_effect(self, player, play_state) -> None:
        """Grants the player a 25% chance to fire an electric projectile."""
        player.has_lightning = True
        player.lightning_chance = 0.25
        player.lightning_damage = 4.0
        
        # Remove this card and add the damage upgrade card to the pool
        play_state.card_manager.unlock_lightning_upgrades()
        