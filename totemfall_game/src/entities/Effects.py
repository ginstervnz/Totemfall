import random
import pygame
from gale.particle_system import ParticleSystem

class BloodEffect:
    def __init__(self, x, y):
        self.active = True
        self.ps = ParticleSystem(x, y, n=10, on_finish=self.finish)
        self.ps.set_life_time(0.1, 0.2)
        self.ps.set_linear_acceleration(-25, -40, 25, 10)
        self.ps.set_area_spread(2, 2)
        self.ps.set_colors([(180, 20, 20, 255), (100, 10, 10, 150)])
        self.ps.generate()
        
    def finish(self):
        self.active = False
        
    def update(self, dt):
        self.ps.update(dt)
        
    def render(self, surface):
        self.ps.render(surface)

class DarkSmokeEffect:
    def __init__(self, x, y):
        self.active = True
        self.ps = ParticleSystem(x, y, n=15, on_finish=self.finish)
        self.ps.set_life_time(0.5, 1.2)
        self.ps.set_linear_acceleration(-30, -60, 30, -20) 
        self.ps.set_area_spread(15, 15)
        self.ps.set_colors([(80, 80, 80, 255), (40, 40, 40, 200), (20, 20, 20, 100)])
        self.ps.generate()
        
    def finish(self):
        self.active = False
        
    def update(self, dt):
        self.ps.update(dt)
        
    def render(self, surface):
        self.ps.render(surface)

class LightningEffect:
    def __init__(self, start_x: float, start_y: float, end_x: float, end_y: float):
        self.active = True
        self.start = (start_x, start_y)
        self.end = (end_x, end_y)
        self.timer = 0.15 # Stays on screen for 150ms
        self.points = [self.start]
        for _ in range(2):
            mid_x = (self.start[0] + self.end[0]) / 2 + random.uniform(-20, 20)
            mid_y = (self.start[1] + self.end[1]) / 2 + random.uniform(-20, 20)
            self.points.append((mid_x, mid_y))
        self.points.append(self.end)

    def update(self, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        if self.active:
            # Draw an intense cyan outer glow (width 3) and a white core (width 1)
            pygame.draw.lines(surface, (0, 255, 255), False, self.points, 3)
            pygame.draw.lines(surface, (255, 255, 255), False, self.points, 1)
