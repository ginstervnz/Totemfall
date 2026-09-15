import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings

class GameOverState(BaseState):
    def enter(self, kill_counts=None, **kwargs) -> None:
        pygame.mouse.set_visible(True)
        self.kill_counts = kill_counts or {}
        self.is_transitioning = False

        # --- FADE IN EFFECT ---
        # Starts fully black (255) and fades to clear (0) over 1.5 seconds
        self.transition_alpha = 255.0
        Timer.tween(1.5, [(self, {'transition_alpha': 0.0})])

    def update(self, dt: float) -> None:
        Timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45))
        
        font_medium = settings.FONTS['medium']
        title_text = font_medium.render("EL OBELISCO HA CAIDO", True, (220, 50, 50))
        title_rect = title_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 25))
        surface.blit(title_text, title_rect)

        font_small = settings.FONTS['small']

        items = list(self.kill_counts.items())
        num_items = len(items)

        if num_items > 0:
            item_width = 58   
            item_height = 32  
            max_cols = 7      
            
            columns = min(num_items, max_cols)
            total_width = columns * item_width
            
            start_x = (settings.VIRTUAL_WIDTH - total_width) // 2
            start_y = 65 
            
            for i, (texture_id, count) in enumerate(items):
                col = i % max_cols    
                row = i // max_cols   
                
                curr_x = start_x + (col * item_width)
                curr_y = start_y + (row * item_height)
                
                if texture_id in settings.TEXTURES:
                    image = settings.TEXTURES[texture_id]
                    frames_id = f"{texture_id}_frames"
                    
                    if frames_id in settings.FRAMES:
                        frame_rect = settings.FRAMES[frames_id][0]
                        enemy_surface = image.subsurface(frame_rect)
                        surface.blit(enemy_surface, (curr_x, curr_y))
                
                count_text = font_small.render(f"x {count}", True, (255, 255, 255))
                surface.blit(count_text, (curr_x + 26, curr_y + 2))

        restart_text = font_small.render("Presiona ENTER para reiniciar", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 20))
        surface.blit(restart_text, restart_rect)

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
                Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('play'))
            elif input_id == 'quit':
                self.is_transitioning = True
                Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('main_menu'))