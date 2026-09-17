import pygame
import json
import urllib.request
import threading
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
import settings

class TopGlobalState(BaseState):
    def enter(self) -> None:
        self.transition_alpha = 255.0
        self.is_transitioning = False
        Timer.tween(1.5, [(self, {'transition_alpha': 0.0})])

        # Network state variables
        self.scores = []
        self.is_loading = True
        self.has_error = False

        # DREAMLO CONFIGURATION
        self.public_code = "6aaaf3fc8f40bb15a88594ef" 
        self.url = f"http://dreamlo.com/lb/{self.public_code}/json"

        # Launch the HTTP request in a separate thread to avoid freezing the frame rate.
        thread = threading.Thread(target=self.fetch_scores)
        thread.start()

    def fetch_scores(self):
        try:
            # We make the request with a 5-second time limit.
            with urllib.request.urlopen(self.url, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                # We navigate the Dreamlo JSON.
                leaderboard = data.get('dreamlo', {}).get('leaderboard', {})
                if leaderboard and 'entry' in leaderboard:
                    entries = leaderboard['entry']
                    # If there is only one score, Dreamlo returns a dict instead of a list.
                    if isinstance(entries, dict):
                        entries = [entries]
                    
                    # Save the Top 10
                    self.scores = entries[:10]
                
                self.is_loading = False
        except Exception as e:
            print(f"Connection error with Dreamlo: {e}")
            self.has_error = True
            self.is_loading = False

    def update(self, dt: float) -> None:
        Timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        # Dark background for the menu
        surface.fill((30, 30, 40))
        
        font_medium = settings.FONTS['medium']
        font_small = settings.FONTS['small']

        # Title
        title = font_medium.render("GLOBAL TOP", True, (255, 215, 0))
        surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, 30))

        # TABLE RENDERING
        start_y = 90
        if self.is_loading:
            loading_txt = font_small.render("Connecting to the Obelisk...", True, (180, 190, 200))
            surface.blit(loading_txt, (settings.VIRTUAL_WIDTH // 2 - loading_txt.get_width() // 2, start_y + 30))
        
        elif self.has_error:
            error_txt = font_small.render("Connection error. Try again later.", True, (220, 50, 50))
            surface.blit(error_txt, (settings.VIRTUAL_WIDTH // 2 - error_txt.get_width() // 2, start_y + 30))
            
        elif not self.scores:
            empty_txt = font_small.render("No one has defended the totem.", True, (180, 190, 200))
            surface.blit(empty_txt, (settings.VIRTUAL_WIDTH // 2 - empty_txt.get_width() // 2, start_y + 30))
            
        else:
            # Plot the scores
            for i, score in enumerate(self.scores):
                # score['name'] and score['score'] are the standard Dreamlo keys.
                name = score.get('name', 'Unknown')
                pts = score.get('score', '0')
                
                # Name left-aligned, score right-aligned
                name_txt = font_small.render(f"{i+1}. {name}", True, (255, 255, 255))
                pts_txt = font_small.render(f"{pts} pts", True, (80, 190, 255))
                
                surface.blit(name_txt, (settings.VIRTUAL_WIDTH // 2 - 120, start_y + (i * 20)))
                surface.blit(pts_txt, (settings.VIRTUAL_WIDTH // 2 + 60, start_y + (i * 20)))

        # Back button
        back_txt = font_small.render("Press ENTER to return", True, (150, 150, 150))
        surface.blit(back_txt, (settings.VIRTUAL_WIDTH // 2 - back_txt.get_width() // 2, settings.VIRTUAL_HEIGHT - 30))

        # --- ALPHA FADE OVERLAY ---
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.transition_alpha))
            surface.blit(fade_surface, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed and not self.is_transitioning:
            if input_id == 'confirm' or input_id == 'quit':
                if hasattr(settings, 'AUDIO_MANAGER'):
                    settings.AUDIO_MANAGER.play_sfx('confirm')
                self.is_transitioning = True
                Timer.tween(1.0, [(self, {'transition_alpha': 255.0})], on_finish=lambda: self.state_machine.change('main_menu'))