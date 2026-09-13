import pygame
from gale.state import BaseState
from gale.input_handler import InputData
import settings

class GameOverState(BaseState):
    def enter(self) -> None:
        pygame.mouse.set_visible(True)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45))
        
        font_medium = settings.FONTS['medium']
        title_text = font_medium.render("EL OBELISCO HA CAIDO", True, (220, 50, 50))
        title_rect = title_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 20))
        surface.blit(title_text, title_rect)

        font_small = settings.FONTS['small']
        restart_text = font_small.render("Presiona ENTER para reiniciar", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 25))
        surface.blit(restart_text, restart_rect)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == 'confirm' and input_data.pressed:
            self.state_machine.change('play')
        elif input_id == 'quit' and input_data.pressed:
            self.state_machine.change('main_menu')