import pygame
import random
import urllib.request
import threading
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings
from src.entities.FireworkEffect import FireworkEffect

class VictoryState(BaseState):
    def enter(self, kill_counts=None,final_score=0, saved_player=None, **kwargs) -> None:
        pygame.mouse.set_visible(True)
        self.kill_counts = kill_counts or {}
        self.final_score = final_score
        self.saved_player = saved_player
        self.is_transitioning = False

        # HORIZONTAL SUBMENU VARIABLES
        self.options = ['Keep Playing', 'Main Menu']
        self.selected_index = 0
        self.input_timer = 0.0

        # SEND TO DREAMLO
        if settings.PLAYER_NAME and self.final_score > 0:
            private_code = "j2m--fCKX0GOnkkhqe2zRgHItq3tEiIkCtlIAozjkI8A"
            safe_name = settings.PLAYER_NAME.replace(" ", "%20")
            url = f"http://dreamlo.com/lb/{private_code}/add/{safe_name}/{self.final_score}"
            
            def push_score():
                try:
                    urllib.request.urlopen(url, timeout=3)
                    print(f"[*] Puntaje enviado a Dreamlo: {safe_name} - {self.final_score}")
                except Exception as e:
                    print(f"[!] Error al enviar a Dreamlo: {e}")
                    
            threading.Thread(target=push_score).start()

        # Fireworks Variables
        self.particle_systems = []
        self.firework_timer = 0.2

        # FADE IN EFFECT
        self.transition_alpha = 255.0
        Timer.tween(1.5, [(self, {'transition_alpha': 0.0})])

    def update(self, dt: float) -> None:
        Timer.update(dt)

        if self.input_timer > 0:
            self.input_timer -= dt

        # Logic for launching fireworks
        self.firework_timer -= dt
        if self.firework_timer <= 0:
            # Next firework at a random time (0.3 to 0.8 sec)
            self.firework_timer = random.uniform(0.3, 0.8)

            # They appear at random positions in the upper half of the screen.
            fx = random.randint(50, settings.VIRTUAL_WIDTH - 50)
            fy = random.randint(20, settings.VIRTUAL_HEIGHT // 2)
            
            self.particle_systems.append(FireworkEffect(fx, fy))
            
        # Update the particles
        for i in range(len(self.particle_systems) - 1, -1, -1):
            self.particle_systems[i].update(dt)
            if not self.particle_systems[i].active:
                self.particle_systems.pop(i)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45))

        for ps in self.particle_systems:
            ps.render(surface)
        
        font_medium = settings.FONTS['medium']
        # Gold title indicating victory
        title_text = font_medium.render("You have saved the world.", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 30))
        surface.blit(title_text, title_rect)

        # DRAWING THE MAGICIAN (Left)
        if 'wizard' in settings.TEXTURES and 'wizard_frames' in settings.FRAMES:
            wizard_img = settings.TEXTURES['wizard']
            wizard_frame = settings.FRAMES['wizard_frames'][0] # Usamos el frame de reposo
            wizard_surf = wizard_img.subsurface(wizard_frame)
            # We place it to the left of the text, with 15 px of spacing.
            wizard_rect = wizard_surf.get_rect(midright=(title_rect.left - 15, title_rect.centery))
            surface.blit(wizard_surf, wizard_rect)
            
        # DRAW THE TOTEM (Right)
        if 'obelisk' in settings.TEXTURES:
            obelisk_img = settings.TEXTURES['obelisk']
            if 'obelisk_frames' in settings.FRAMES:
                obelisk_frame = settings.FRAMES['obelisk_frames'][0]
                obelisk_surf = obelisk_img.subsurface(obelisk_frame)
            else:
                obelisk_surf = obelisk_img
                
            # We place it to the right of the text, with a 15 px gap.
            obelisk_rect = obelisk_surf.get_rect(midleft=(title_rect.right + 15, title_rect.centery))
            surface.blit(obelisk_surf, obelisk_rect)



        font_small = settings.FONTS['small']

        # Show the score
        score_txt = font_small.render(f"Final Score: {self.final_score}", True, (80, 190, 255))
        surface.blit(score_txt, (settings.VIRTUAL_WIDTH // 2 - score_txt.get_width() // 2, 50))

        items = list(self.kill_counts.items())
        num_items = len(items)

        # Statistics grid
        if num_items > 0:
            item_width = 58
            item_height = 32
            max_cols = 7
            
            columns = min(num_items, max_cols)
            total_width = columns * item_width
            
            start_x = (settings.VIRTUAL_WIDTH - total_width) // 2
            start_y = 75
            
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

        # CURSOR EXTRACTION
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

        # HORIZONTAL SUBMENU RENDERING
        option_y = settings.VIRTUAL_HEIGHT - 20
        positions_x = [settings.VIRTUAL_WIDTH * 0.35, settings.VIRTUAL_WIDTH * 0.70]

        for i, option in enumerate(self.options):
            color = (80, 190, 255) if i == self.selected_index else (180, 190, 200)
                
            option_shadow = font_small.render(option, True, (0, 0, 0))
            shadow_rect = option_shadow.get_rect(center=(positions_x[i] + 2, option_y + 2))
            surface.blit(option_shadow, shadow_rect)
            
            option_surface = font_small.render(option, True, color)
            rect = option_surface.get_rect(center=(positions_x[i], option_y))
            surface.blit(option_surface, rect)
            
            if i == self.selected_index and cursor_surf:
                cursor_rect = cursor_surf.get_rect(midleft=(rect.right + 10, rect.centery))
                surface.blit(cursor_surf, cursor_rect)

        # ALPHA FADE OVERLAY
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.transition_alpha))
            surface.blit(fade_surface, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        # We prevent double input.
        if input_data.pressed and not self.is_transitioning:

            if self.input_timer > 0:
                return
            
            if input_id in ['right', 'left']:
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('hover')
                self.input_timer = 0.15 
                
                if input_id == 'right':
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif input_id == 'left':
                    self.selected_index = (self.selected_index - 1) % len(self.options)

            elif input_id == 'confirm':
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('confirm')
                
                self.is_transitioning = True
                selected_option = self.options[self.selected_index]
                
                if selected_option == 'Keep Playing':
                    # We send the signal randomly here.
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], 
                                on_finish=lambda: self.state_machine.change('play', random_mode=True, previous_score=self.final_score, previous_kills=self.kill_counts, saved_player=self.saved_player))
                                
                elif selected_option == 'Main Menu':
                    Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], 
                                on_finish=lambda: self.state_machine.change('main_menu'))