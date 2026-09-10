import pygame
import math
from gale.state import StateMachine
from gale.animation import Animation
import settings
from src.entities.player.PlayerIdleState import PlayerIdleState
from src.entities.player.PlayerWalkState import PlayerWalkState

class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 26
        self.height = 18
        self.speed = 100
        self.facing_right = True

        #Shot 
        self.fire_rate = 0.5 
        self.shoot_timer = self.fire_rate
        self.just_fired = False


        self.animations = {
            'idle': Animation([0], 1), 
            'walk': Animation([1, 2, 3], 0.15)
        }
        self.current_animation = self.animations['idle']
        self.state_machine = StateMachine({
            'idle': lambda sm: PlayerIdleState(self, sm),
            'walk': lambda sm: PlayerWalkState(self, sm)
        })
        self.state_machine.change('idle')

    def change_animation(self, animation_id: str) -> None:
        self.current_animation = self.animations[animation_id]

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)
        self.current_animation.update(dt)

        #Shot logic
        self.just_fired = False
        self.shoot_timer -= dt
        
        if self.shoot_timer <= 0:
            self.shoot_timer = self.fire_rate 
            self.just_fired = True
            
            mx, my = pygame.mouse.get_pos()
            virtual_mx = mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)
            virtual_my = my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)
            
            center_x = self.x + (self.width / 2)
            center_y = self.y + (self.height / 2)
            
            angle = math.atan2(virtual_my - center_y, virtual_mx - center_x)
            
            #Only debuging
            print(f"PUM! Bala generada en ángulo: {math.degrees(angle):.2f} grados")

    def render(self, surface: pygame.Surface) -> None:
        image = settings.TEXTURES['wizard']
        frame_idx = self.current_animation.get_current_frame()
        frame_rect = settings.FRAMES['wizard_frames'][frame_idx]
        wizard_surface = image.subsurface(frame_rect)
        
        if not self.facing_right:
            wizard_surface = pygame.transform.flip(wizard_surface, True, False)
            
        surface.blit(wizard_surface, (self.x, self.y))