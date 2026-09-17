import pygame
import random
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
from gale.animation import Animation
import settings

# --- HELPER CLASS FOR GALE TWEENS ---
class CinematicActor:
    """A simple data class with a scale attribute for dramatic close-ups."""
    def __init__(self, x: float, y: float, anim: Animation, tex_id: str = None, frame_key: str = None, scale: float = 2.0):
        self.x = x
        self.y = y
        self.anim = anim
        self.tex_id = tex_id
        self.frame_key = frame_key
        self.scale = scale

class IntroCinematicState(BaseState):
    def enter(self) -> None:
        self.text_alpha = 0.0
        self.fade_alpha = 255.0
        
        # Center of the screen for the dramatic run
        self.center_y = (settings.VIRTUAL_HEIGHT // 2) - 40
        
        # --- ACTORS SETUP ---
        # The Wizard starts off-screen to the left, scaled 2x
        self.wizard = CinematicActor(
            x=-100.0, 
            y=self.center_y, 
            anim=Animation([0, 1, 2, 3], 0.12),
            tex_id='wizard',
            frame_key='wizard_frames',
            scale=2.0
        )
        
        # Generate a MASSIVE random horde trailing far behind
        self.horde = []
        enemy_types = [
            ('goblin', 'goblin_frames'), 
            ('minotaur', 'minotaur_frames'), 
            ('skeleton', 'skeleton_frames'),
            ('slime', 'slime_frames'),
            ('batilisk', 'batilisk_frames')
        ]
        
        # Spawn 40 monsters to create a true stampede
        for i in range(40):
            tex, frames = random.choice(enemy_types)
            
            # Stagger them densely: base offset + tight spacing + random noise
            start_x = -150 - (i * 60) - random.randint(0, 50)
            
            # Spread them across the vertical axis
            start_y = self.center_y + random.randint(-50, 70)
            
            # Slightly vary animation speed so they don't look perfectly synchronized
            anim_speed = random.uniform(0.08, 0.14)
            
            self.horde.append(CinematicActor(
                x=start_x, 
                y=start_y, 
                anim=Animation([0, 1, 2, 3], anim_speed), 
                tex_id=tex, 
                frame_key=frames,
                scale=2.0 
            ))

        # --- PARTICLES ---
        self.particles = []
        self.particle_timer = 0.0

        # --- CHOREOGRAPHY (THE TWEENS & TIMING) ---
        # Total Cinematic Duration: ~11.0 seconds
        
        # 1. Fade screen in slowly from black (1.5s)
        Timer.tween(1.5, [(self, {'fade_alpha': 0.0})])
        
        # 2. Text fades in, stays longer to read, then fades out
        Timer.after(1.0, lambda: Timer.tween(1.5, [(self, {'text_alpha': 255.0})]))
        Timer.after(4.5, lambda: Timer.tween(1.0, [(self, {'text_alpha': 0.0})]))
        
        # 3. Wizard starts running after text fades (takes 3.5s to cross)
        def start_wizard_run():
            Timer.tween(3.5, [(self.wizard, {'x': settings.VIRTUAL_WIDTH + 150})])
        Timer.after(5.5, start_wizard_run)
        
        # 4. Massive Horde chases the wizard
        def start_horde_run():

            if 'chase' in settings.AUDIO_MANAGER.sounds:
                settings.AUDIO_MANAGER.sounds['chase'].play(loops=-1)
            
            tweens = []
            for enemy in self.horde:
                # Move everyone a fixed distance so they all run at a similar, steady speed
                target_x = enemy.x + 2500 
                tweens.append((enemy, {'x': target_x}))
                
            # The horde moves constantly for 10 seconds
            Timer.tween(10.0, tweens)
            
        # Horde starts slightly after the wizard
        Timer.after(6.0, start_horde_run)
        
        # 5. HARD CUT: Transition to the game while the horde is still filling the screen
        Timer.after(11.0, self.start_game)

    def start_game(self) -> None:
        """Cleans up timers and transitions to the actual gameplay."""
        if 'chase' in settings.AUDIO_MANAGER.sounds:
            settings.AUDIO_MANAGER.sounds['chase'].fadeout(500)
        Timer.clear()
        self.state_machine.change('play')

    def update(self, dt: float) -> None:
        Timer.update(dt)
        
        # Update animations
        self.wizard.anim.update(dt)
        for enemy in self.horde:
            enemy.anim.update(dt)
            
        # --- WHITE DUST PARTICLES LOGIC ---
        # Spawn dust if the wizard is actively moving across the screen
        if -50 < self.wizard.x < settings.VIRTUAL_WIDTH:
            self.particle_timer += dt
            if self.particle_timer > 0.02: 
                self.particle_timer = 0.0
                
                wizard_foot_y = self.wizard.y + 36 
                wizard_back_x = self.wizard.x + 10
                
                self.particles.append({
                    'x': wizard_back_x,
                    'y': wizard_foot_y + random.randint(-5, 5),
                    'vx': random.uniform(-30, -10), 
                    'vy': random.uniform(-10, 5),   
                    'life': 0.3,
                    'max_life': 0.3,
                    'size': random.randint(3, 6)
                })
                
        # Update and cull particles
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            
        self.particles = [p for p in self.particles if p['life'] > 0]

    def render(self, surface: pygame.Surface) -> None:
        # Dark cinematic background
        surface.fill((15, 10, 20))
        
        # Render Dust Particles
        for p in self.particles:
            alpha = max(0, int(255 * (p['life'] / p['max_life'])))
            p_surf = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
            p_surf.fill((255, 255, 255, alpha))
            surface.blit(p_surf, (p['x'], p['y']))
            
        # Render Helper Function
        def draw_actor(actor):
            tex = settings.TEXTURES[actor.tex_id]
            rect = settings.FRAMES[actor.frame_key][actor.anim.get_current_frame()]
            surf = tex.subsurface(rect)
            
            # Apply dynamic scaling
            if actor.scale != 1.0:
                new_w = int(rect.width * actor.scale)
                new_h = int(rect.height * actor.scale)
                surf = pygame.transform.scale(surf, (new_w, new_h))
                
            surface.blit(surf, (actor.x, actor.y))

        # Render Horde first
        for enemy in self.horde:
            draw_actor(enemy)
            
        # Render Wizard on top
        draw_actor(self.wizard)
            
        # --- RENDER CENTERED TEXT IN TWO LINES ---
        font_med = settings.FONTS['medium']
        font_small = settings.FONTS['small']
        
        text_1 = font_med.render("THE HORDE APPROACHES...", True, (200, 50, 50))
        text_2 = font_small.render("DEFEND THE TOTEM!", True, (255, 100, 100))
        
        text_1.set_alpha(int(self.text_alpha))
        text_2.set_alpha(int(self.text_alpha))
        
        t1_x = (settings.VIRTUAL_WIDTH // 2) - (text_1.get_width() // 2)
        t1_y = (settings.VIRTUAL_HEIGHT // 3) - 20
        
        t2_x = (settings.VIRTUAL_WIDTH // 2) - (text_2.get_width() // 2)
        t2_y = t1_y + text_1.get_height() + 5
        
        surface.blit(text_1, (t1_x, t1_y))
        surface.blit(text_2, (t2_x, t2_y))
        
        # Render Scene Fade
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(int(self.fade_alpha))
            surface.blit(fade_surf, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        # Allow the player to skip the cutscene by pressing ENTER
        if input_id == 'confirm' and input_data.pressed:
            self.start_game()