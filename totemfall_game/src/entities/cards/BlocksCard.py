from src.entities.BaseCard import BaseCard

class BlocksCard(BaseCard):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 'Block', 'Destroy', 'icon_blocks', 'card_base_3')

    def apply_effect(self, player, play_state) -> None:
        """Grants the player the ability to destroy specific blocks."""
        player.can_destroy_blocks = True
        play_state.card_manager.remove_card(self.__class__)
        
        import settings
        if 'confirm' in settings.AUDIO_MANAGER.sounds:
            settings.AUDIO_MANAGER.play_sfx('confirm')