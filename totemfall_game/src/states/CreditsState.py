import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings

class CreditsState(BaseState):
    def enter(self) -> None:
        # Start fully black and fade into the scene
        self.transition_alpha = 255.0
        self.is_transitioning = False
        
        Timer.tween(1.0, [(self, {'transition_alpha': 0.0})])

        # Define the structure of the credits screen: (Text, Font Size, Color)
        self.credits_lines = [
            ("ASSET CREATORS", 'medium', (255, 215, 0)), 
            ("", 'small', (255, 255, 255)), # Spacer
            ("Reaktori - CC0 License", 'small', (200, 200, 200)),
            ("Batareya - Free & Commercial License", 'small', (200, 200, 200)),
            ("Atelier Pixerelia - Standard Asset License", 'small', (200, 200, 200)),
            ("", 'small', (255, 255, 255)), # Spacer
            ("Thank you for sharing your art with the community!", 'small', (80, 190, 255)),
            ("", 'small', (255, 255, 255)), # Spacer
            ("Press ENTER to return", 'small', (100, 100, 100))
        ]

    def update(self, dt: float) -> None:
        Timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        # Render a dark background
        surface.fill((20, 20, 25))
        
        # SPACING AND ANCHORING ---
        line_spacing = 25
        total_height = len(self.credits_lines) * line_spacing
        
        # Add a +10 padding at the end so it doesn't touch the absolute top edge
        start_y = (settings.VIRTUAL_HEIGHT // 2) - (total_height // 2) + 10

        for i, (text, font_key, color) in enumerate(self.credits_lines):
            if text == "":
                continue
                
            font = settings.FONTS[font_key]
            
            # Use 'midtop' instead of 'center' to prevent vertical clipping
            shadow_surf = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect(midtop=(settings.VIRTUAL_WIDTH // 2 + 2, start_y + (i * line_spacing) + 2))
            surface.blit(shadow_surf, shadow_rect)
            
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(midtop=(settings.VIRTUAL_WIDTH // 2, start_y + (i * line_spacing)))
            surface.blit(text_surf, text_rect)

        # Render Scene Fade Overlay
        if self.transition_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(int(self.transition_alpha))
            surface.blit(fade_surf, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        # Return to main menu on confirmation
        if input_data.pressed and not self.is_transitioning:
            if input_id == 'confirm':
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('confirm')
                    
                self.is_transitioning = True
                
                # Fade to black, then swap state
                Timer.tween(2.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('main_menu'))