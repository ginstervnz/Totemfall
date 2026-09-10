import pygame
from gale.state import BaseState
from gale.input_handler import InputData
import settings

class MainMenuState(BaseState):
    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 30, 40))
        title = settings.FONTS['medium'].render("TOTEMFALL", True, (255, 255, 255))
        prompt = settings.FONTS['small'].render("Presiona ENTER para jugar", True, (200, 200, 200))
        surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, settings.VIRTUAL_HEIGHT // 3))
        surface.blit(prompt, (settings.VIRTUAL_WIDTH // 2 - prompt.get_width() // 2, settings.VIRTUAL_HEIGHT // 2))
        
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed:
            if input_id == 'confirm':
                self.state_machine.change('play')
            elif input_id == 'options':
                self.state_machine.change('options')