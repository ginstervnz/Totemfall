import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings

class MainMenuState(BaseState):
    def enter(self) -> None:
        self.transition_alpha = 0.0
        self.is_transitioning = False

    def update(self, dt: float) -> None:
        Timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 30, 40))
        title = settings.FONTS['medium'].render("TOTEMFALL", True, (255, 255, 255))
        prompt = settings.FONTS['small'].render("Presiona ENTER para jugar", True, (200, 200, 200))
        surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, settings.VIRTUAL_HEIGHT // 3))
        surface.blit(prompt, (settings.VIRTUAL_WIDTH // 2 - prompt.get_width() // 2, settings.VIRTUAL_HEIGHT // 2))
        
        # --- ALPHA FADE OVERLAY ---
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.transition_alpha))
            surface.blit(fade_surface, (0, 0))
        
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed and not self.is_transitioning:
            if input_id == 'confirm':
                settings.AUDIO_MANAGER.play_sfx('confirm')
                self.is_transitioning = True
                # Fade to black over 1 second, then change state
                Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('intro'))
            elif input_id == 'options':
                self.state_machine.change('options')