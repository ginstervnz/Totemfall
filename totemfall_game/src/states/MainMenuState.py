import pygame
import sys
import math
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings

class MainMenuState(BaseState):
    def enter(self) -> None:
        self.transition_alpha = 0.0
        self.is_transitioning = False

        # List of options and selection tracker
        self.options = ['Play', 'Global Top', 'Change Name' , 'Exit']
        self.selected_index = 0

        # Timer for our pulse effect
        self.time_alive = 0.0
        self.input_timer = 0.0

        # Load and scale the background ONCE for maximum efficiency.
        if 'menu_bg' in settings.TEXTURES:
            raw_bg = settings.TEXTURES['menu_bg']
            self.bg_image = pygame.transform.scale(raw_bg, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        else:
            self.bg_image = None

    def update(self, dt: float) -> None:
        Timer.update(dt)
        self.time_alive += dt

        if self.input_timer > 0:
            self.input_timer -= dt

    def render(self, surface: pygame.Surface) -> None:

        if getattr(self, 'bg_image', None):
            surface.blit(self.bg_image, (0, 0))

            # Dark semi-transparent filter to provide contrast
            dark_overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 100)) 
            surface.blit(dark_overlay, (0, 0))


        else:
            # Fallback (solid color) in case the image is missing
            surface.fill((30, 30, 40))

       # Drop Shadow and Title Rendering
        title_font = settings.FONTS['medium']
        title_str = "TOTEMFALL"
        
        # Black shadow (offset +2px on X and +2px on Y)
        title_shadow = title_font.render(title_str, True, (0, 0, 0))
        surface.blit(title_shadow, (settings.VIRTUAL_WIDTH // 2 - title_shadow.get_width() // 2 + 2, settings.VIRTUAL_HEIGHT // 4 + 2))
        
        # Actual white text
        title = title_font.render(title_str, True, (255, 255, 255))
        surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, settings.VIRTUAL_HEIGHT // 4))

        # Extract the cursor sprite
        if 'cursor' in settings.TEXTURES and 'cursor_frames' in settings.FRAMES:
            cursor_img = settings.TEXTURES['cursor']
            cursor_frame = settings.FRAMES['cursor_frames'][0]
            original_cursor = cursor_img.subsurface(cursor_frame)
            # Reduce the cursor size
            scale_factor = 0.75 

            new_width = int(original_cursor.get_width() * scale_factor)
            new_height = int(original_cursor.get_height() * scale_factor)
            # We use `scale` instead of `smoothscale` to avoid losing the sharpness of the pixel art.
            cursor_surf = pygame.transform.scale(original_cursor, (new_width, new_height))
        else:
            cursor_surf = None

        # Render the options dynamically
        start_y = settings.VIRTUAL_HEIGHT // 2
        for i, option in enumerate(self.options):
            if i == self.selected_index:
                color = (80, 190, 255) # Bright Blue (Mage)
            else:
                color = (180, 190, 200) # grey

            display_text = option

            option_font = settings.FONTS['small']
                
            # Shadow for the options
            option_shadow = option_font.render(display_text, True, (0, 0, 0))
            shadow_rect = option_shadow.get_rect(center=(settings.VIRTUAL_WIDTH // 2 + 2, start_y + (i * 35) + 2))
            surface.blit(option_shadow, shadow_rect)
            
            # Colored text
            option_surface = option_font.render(display_text, True, color)
            rect = option_surface.get_rect(center=(settings.VIRTUAL_WIDTH // 2, start_y + (i * 35))) 
            surface.blit(option_surface, rect)

            # Draw the cursor pointing to the selected option.
            if i == self.selected_index and cursor_surf:
                cursor_rect = cursor_surf.get_rect(midleft=(rect.right + 10, rect.centery))
                surface.blit(cursor_surf, cursor_rect)

        # RENDER THE VERSION WITH PULSE
        pulse = int(177 + 77 * math.sin(self.time_alive * 4)) 
        version_color = (pulse, pulse, pulse)

        # We're putting the version here.
        version_text = settings.FONTS['small'].render("v0.5.0", True, version_color)
        
        # Anclamos el rectángulo a la esquina inferior derecha (restamos 10px para que respire)
        version_rect = version_text.get_rect(bottomright=(settings.VIRTUAL_WIDTH - 10, settings.VIRTUAL_HEIGHT - 10))
        surface.blit(version_text, version_rect)
        
        # --- ALPHA FADE OVERLAY ---
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.transition_alpha))
            surface.blit(fade_surface, (0, 0))
        
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed and not self.is_transitioning:

            if self.input_timer > 0:
                return

            # Menu navigation
            if input_id == 'down':
                self.selected_index = (self.selected_index + 1) % len(self.options)
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('hover') # Sound when moving
                self.input_timer = 0.15
                    
            elif input_id == 'up':
                self.selected_index = (self.selected_index - 1) % len(self.options)
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('hover') # Sonido al moverse
                self.input_timer = 0.1
            
            # Selection routing
            elif input_id == 'confirm':
                selected_option = self.options[self.selected_index]
                
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('confirm')
                self.is_transitioning = True
                
                # Depending on the option, we fade out to a different destination.
                if selected_option == 'Play':
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('play'))
                elif selected_option == 'Global Top':
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('top'))
                elif selected_option == 'Change Name':
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('name'))
                elif selected_option == 'Exit':
                    # exit from the game
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=self.quit_game)

    def quit_game(self):
        pygame.quit()
        sys.exit()