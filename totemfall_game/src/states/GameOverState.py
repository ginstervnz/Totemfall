import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings

class GameOverState(BaseState):
    def enter(self, kill_counts=None, **kwargs) -> None:
        pygame.mouse.set_visible(True)
        self.kill_counts = kill_counts or {}

        # Fade In
        self.transition_radius = 0.0
        Timer.tween(1.5, [
            (self, {'transition_radius': 350.0})
        ])

    def update(self, dt: float) -> None:
        Timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45))
        
        font_medium = settings.FONTS['medium']
        title_text = font_medium.render("EL OBELISCO HA CAIDO", True, (220, 50, 50))
        title_rect = title_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 25))
        surface.blit(title_text, title_rect)

        font_small = settings.FONTS['small']

        # Centered Horizontal Rendering
        items = list(self.kill_counts.items())
        num_items = len(items)

        if num_items > 0:
            item_width = 58   # Horizontal space per enemy
            item_height = 32  # Vertical spacing between rows
            max_cols = 7      # Maximum enemies per row
            
            # We calculate the total width based on a maximum of 5 columns to center the block.
            columns = min(num_items, max_cols)
            total_width = columns * item_width
            
            start_x = (settings.VIRTUAL_WIDTH - total_width) // 2
            start_y = 65 # We raised the starting point a bit so that several rows would fit.
            
            for i, (texture_id, count) in enumerate(items):
                # Grid Math:
                col = i % max_cols    # It returns 0, 1, 2, 3, 4 and then resets to 0.
                row = i // max_cols   # Returns 0 for the first 5, then 1 for the next 5
                
                curr_x = start_x + (col * item_width)
                curr_y = start_y + (row * item_height)
                
                # Draw the enemy sprite
                if texture_id in settings.TEXTURES:
                    image = settings.TEXTURES[texture_id]
                    frames_id = f"{texture_id}_frames"
                    
                    if frames_id in settings.FRAMES:
                        frame_rect = settings.FRAMES[frames_id][0]
                        enemy_surface = image.subsurface(frame_rect)
                        surface.blit(enemy_surface, (curr_x, curr_y))
                
                # Draw the text "x N"
                count_text = font_small.render(f"x {count}", True, (255, 255, 255))
                surface.blit(count_text, (curr_x + 26, curr_y + 2))

        restart_text = font_small.render("Presiona ENTER para reiniciar", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 20))
        surface.blit(restart_text, restart_rect)

        # Iris wipe effect to reveal the Game Over.
        if hasattr(self, 'transition_radius') and self.transition_radius < 350:
            iris_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            iris_surface.fill((0, 0, 0))
            
            center_x = settings.VIRTUAL_WIDTH // 2
            center_y = settings.VIRTUAL_HEIGHT // 2
            
            safe_radius = max(0, int(self.transition_radius))
            COLOR_KEY = (255, 0, 255)
            
            pygame.draw.circle(iris_surface, COLOR_KEY, (center_x, center_y), safe_radius)
            iris_surface.set_colorkey(COLOR_KEY)
            
            surface.blit(iris_surface, (0, 0))


    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == 'confirm' and input_data.pressed:
            self.state_machine.change('play')
        elif input_id == 'quit' and input_data.pressed:
            self.state_machine.change('main_menu')