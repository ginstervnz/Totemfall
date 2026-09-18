import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings
import random

class NameInputState(BaseState):
    def enter(self, force_input: bool = False) -> None:
        self.chars = [65, 65, 65, 65, 65] # ASCII codes for "A A A A A"
        self.cursor_pos = 0 # Which letter we are editing (0 to 4), 5 (Save), 6 (Cancel)
        self.is_transitioning = False
        self.transition_alpha = 0.0
        self.input_timer = 0.0
        self.force_input = force_input

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

        # CURSOR EXTRACTION FOR THE MENU
        if 'cursor' in settings.TEXTURES and 'cursor_frames' in settings.FRAMES:
            cursor_img = settings.TEXTURES['cursor']
            cursor_frame = settings.FRAMES['cursor_frames'][0]
            original_cursor = cursor_img.subsurface(cursor_frame)
            scale_factor = 0.75 
            new_width = int(original_cursor.get_width() * scale_factor)
            new_height = int(original_cursor.get_height() * scale_factor)
            cursor_surf = pygame.transform.scale(original_cursor, (new_width, new_height))
        else:
            cursor_surf = None

        option_y = settings.VIRTUAL_HEIGHT - 40

        # Depending on the flag, we hide 'Cancel' and center 'Save'.
        if self.force_input:
            options = ['Save']
            positions_x = [settings.VIRTUAL_WIDTH * 0.5]
        else:
            # HORIZONTAL SUBMENU RENDERING
            options = ['Save', 'Cancel']
            positions_x = [settings.VIRTUAL_WIDTH * 0.35, settings.VIRTUAL_WIDTH * 0.65]

        for i, option in enumerate(options):
            # Position 5 is 'Save' (index 0), Position 6 is 'Cancel' (index 1)
            is_selected = (self.cursor_pos == i + 5)
            color = (80, 190, 255) if is_selected else (150, 150, 150)
            
            option_shadow = font_small.render(option, True, (0, 0, 0))
            shadow_rect = option_shadow.get_rect(center=(positions_x[i] + 2, option_y + 2))
            surface.blit(option_shadow, shadow_rect)
            
            option_surface = font_small.render(option, True, color)
            rect = option_surface.get_rect(center=(positions_x[i], option_y))
            surface.blit(option_surface, rect)
            
            if is_selected and cursor_surf:
                cursor_rect = cursor_surf.get_rect(midleft=(rect.right + 10, rect.centery))
                surface.blit(cursor_surf, cursor_rect)

        info_text = "ARROWS to edit. ENTER to confirm." if self.force_input else "ARROWS to edit. ENTER to confirm. ESC to Cancel."
        info = font_small.render(info_text, True, (150, 150, 150))
        surface.blit(info, (settings.VIRTUAL_WIDTH // 2 - info.get_width() // 2, settings.VIRTUAL_HEIGHT - 15))

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

                max_cursor = 5 if self.force_input else 6
                
                if input_id == 'right':
                    self.cursor_pos = min(6, self.cursor_pos + 1)
                elif input_id == 'left':
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif input_id == 'up':
                    if self.cursor_pos < 5:
                        # Advance the letter (A -> B -> C). 90 is 'Z'.
                        self.chars[self.cursor_pos] = 65 if self.chars[self.cursor_pos] == 90 else self.chars[self.cursor_pos] + 1
                elif input_id == 'down':
                    if self.cursor_pos < 5:
                        # Go back one letter (C -> B -> A)
                        self.chars[self.cursor_pos] = 90 if self.chars[self.cursor_pos] == 65 else self.chars[self.cursor_pos] - 1
                    
            elif input_id == 'confirm':
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('confirm')

                # LOGICAL ROUTING: If set to 'Cancel' or the exit key is pressed
                if self.cursor_pos == 6:
                    self.is_transitioning = True
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('main_menu'))
                    return
                
                # LOGICAL ROUTING: If you press ENTER on the letters (0–4) or on 'Save' (5)
                self.is_transitioning = True
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

            elif input_id == 'quit':
                if not self.force_input:
                    self.is_transitioning = True
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('main_menu'))