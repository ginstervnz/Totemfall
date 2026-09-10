import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from src.entities.player.Player import Player

import settings

class PlayState(BaseState):
    def enter(self) -> None:
        self.platform_y = 1 
        wizard_x = settings.VIRTUAL_WIDTH // 2
        wizard_y = self.platform_y  
        self.player = Player(wizard_x, wizard_y)

        # Cursor
        pygame.mouse.set_visible(False)
        self.cursor_frame = 3

    def update(self, dt: float) -> None:
        self.player.update(dt)

        #Cursor
        if self.player.just_fired:
            self.cursor_frame = 4
        else:
            self.cursor_frame = 3

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45)) 
        
        stairs_img = settings.TEXTURES['stairs']
        scaled_stairs = pygame.transform.scale(stairs_img, (settings.VIRTUAL_WIDTH, stairs_img.get_height()))
        surface.blit(scaled_stairs, (0, self.platform_y))
        self.player.render(surface)

        #Cursor
        mx, my = pygame.mouse.get_pos()
        virtual_mx = mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)
        virtual_my = my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)
        cursor_img = settings.TEXTURES['cursor']
        frame_rect = settings.FRAMES['cursor_frames'][self.cursor_frame]
        cursor_surf = cursor_img.subsurface(frame_rect)
        surface.blit(cursor_surf, (virtual_mx - (frame_rect.width / 2), virtual_my - (frame_rect.height / 2)))

        
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == 'quit' and input_data.pressed:
            pygame.mouse.set_visible(True)
            self.state_machine.change('main_menu')