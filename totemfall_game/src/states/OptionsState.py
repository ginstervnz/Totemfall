import pygame
from gale.state import BaseState
from gale.input_handler import InputData

class OptionsState(BaseState):
    def render(self, surface: pygame.Surface) -> None:
        surface.fill((50, 40, 50)) 
        
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed and input_id == 'enter':
            self.state_machine.change('main_menu')