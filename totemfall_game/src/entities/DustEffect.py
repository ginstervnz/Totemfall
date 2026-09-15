import pygame
import random

class DustEffect:
    def __init__(self, x: float, y: float):
        self.particles = []
        for _ in range(10):
            self.particles.append({
                'x': x + random.uniform(-15, 15),
                'y': y + random.uniform(-5, 5),
                'vx': random.uniform(-40, 40), 
                'vy': random.uniform(-10, -30), 
                'timer': random.uniform(0.3, 0.6),
                'max_timer': 0.6,
                'radius': random.uniform(3, 7)
            })
        self.active = True

    def update(self, dt: float) -> None:
        self.active = False
        for p in self.particles:
            if p['timer'] > 0:
                p['timer'] -= dt
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['radius'] += 10 * dt
                self.active = True

    def render(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            if p['timer'] > 0:
                alpha = int((p['timer'] / p['max_timer']) * 150)
                color = (200, 200, 190, alpha) 
                surf = pygame.Surface((int(p['radius'] * 2), int(p['radius'] * 2)), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (int(p['radius']), int(p['radius'])), int(p['radius']))
                surface.blit(surf, (p['x'] - p['radius'], p['y'] - p['radius']))