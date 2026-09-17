import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings
import random

class NameInputState(BaseState):
    def enter(self) -> None:
        self.chars = [65, 65, 65, 65, 65] # ASCII codes for "A A A A A"
        self.cursor_pos = 0 # Which letter we are editing (0 to 4)
        self.is_transitioning = False
        self.transition_alpha = 0.0
        self.input_timer = 0.0

    def update(self, dt: float) -> None:
        Timer.update(dt)
        if self.input_timer > 0:
            self.input_timer -= dt

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45))
        
        font_medium = settings.FONTS['medium']
        font_small = settings.FONTS['small']

        title = font_medium.render("Enter your name", True, (255, 215, 0))
        surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, 40))

        # Draw the 5 letters.
        start_x = settings.VIRTUAL_WIDTH // 2 - 60
        for i, char_code in enumerate(self.chars):
            # Bright blue if the cursor is there, gray if not.
            color = (80, 190, 255) if i == self.cursor_pos else (200, 200, 200)
            letter_txt = font_medium.render(chr(char_code), True, color)
            surface.blit(letter_txt, (start_x + (i * 25), 100))
            
            # Underline the active letter.
            if i == self.cursor_pos:
                pygame.draw.rect(surface, (80, 190, 255), (start_x + (i * 25), 135, 18, 3))

        info = font_small.render("Use the ARROWS to change. Press ENTER to confirm.", True, (150, 150, 150))
        surface.blit(info, (settings.VIRTUAL_WIDTH // 2 - info.get_width() // 2, settings.VIRTUAL_HEIGHT - 30))

        # Alpha Fade Overlay
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.transition_alpha))
            surface.blit(fade_surface, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed and not self.is_transitioning:

            if self.input_timer > 0:
                return

            if input_id in ['right', 'left', 'up', 'down']:

                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('hover')

                self.input_timer = 0.15
                
                if input_id == 'right':
                    self.cursor_pos = min(4, self.cursor_pos + 1)
                elif input_id == 'left':
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif input_id == 'up':
                    # Advance the letter (A -> B -> C). 90 is 'Z'.
                    self.chars[self.cursor_pos] = 65 if self.chars[self.cursor_pos] == 90 else self.chars[self.cursor_pos] + 1
                elif input_id == 'down':
                    # Go back one letter (C -> B -> A)
                    self.chars[self.cursor_pos] = 90 if self.chars[self.cursor_pos] == 65 else self.chars[self.cursor_pos] - 1
                    
            elif input_id == 'confirm':
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('confirm')
                self.is_transitioning = True
                    
                # We transform the list of ASCII codes into a string.
                base_name = "".join([chr(c) for c in self.chars])

                pin = random.randint(1000, 9999)
                final_name = f"{base_name}-{pin}"

                try:
                    print(f"[*] Intentando guardar el nombre: {final_name}...")
                        
                    if hasattr(settings, 'save_player_name'):
                        settings.save_player_name(final_name)
                        print("[*] ¡Guardado exitoso en disco!")
                    else:
                        print("[!] ADVERTENCIA: La función 'save_player_name' no existe en settings.py")
                            
                except Exception as e:
                    # Si algo explota (falta de imports, permisos, etc), lo atrapamos aquí
                    print(f"[!] ERROR CRÍTICO AL GUARDAR: {e}")
                    
                # Pase lo que pase arriba, forzamos la transición al menú
                Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('main_menu'))