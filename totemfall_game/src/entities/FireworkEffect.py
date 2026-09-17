import random
from gale.particle_system import ParticleSystem

class FireworkEffect:
    def __init__(self, x, y):
        self.active = True
        self.ps = ParticleSystem(x, y, n=40, on_finish=self.finish) 
        self.ps.set_life_time(0.5, 1.2) 
        
        self.ps.set_linear_acceleration(-80, -80, 80, 80)
        self.ps.set_area_spread(4, 4)
        
        colors = [
            [(255, 215, 0, 255), (255, 140, 0, 0)],   
            [(0, 255, 255, 255), (0, 100, 255, 0)],   
            [(255, 0, 255, 255), (100, 0, 255, 0)],   
            [(50, 255, 50, 255), (0, 150, 0, 0)]      
        ]
        self.ps.set_colors(random.choice(colors))
        self.ps.generate()
        
    def finish(self):
        self.active = False
        
    def update(self, dt):
        self.ps.update(dt)
        
    def render(self, surface):
        self.ps.render(surface)