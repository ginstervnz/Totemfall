import pygame
import math
from gale.state import StateMachine
from gale.animation import Animation
import settings
from src.entities.player.state.PlayerIdleState import PlayerIdleState
from src.entities.player.state.PlayerWalkState import PlayerWalkState

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
        self.cast_animation_timer = 0


        self.animations = {
            'idle': Animation([0], 1), 
            'walk': Animation([1, 2, 3], 0.15),
            'cast': Animation([4,5], 0.05)
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
        self.animations['cast'].update(dt)

        if self.cast_animation_timer > 0:
            self.cast_animation_timer -= dt

        #Shot logic
        self.just_fired = False
        self.shoot_timer -= dt
        
        if self.shoot_timer <= 0:
            self.shoot_timer = self.fire_rate 
            self.just_fired = True

            self.cast_animation_timer = 0.15 
            self.animations['cast'] = Animation([4,5], 0.05)
            
            mx, my = pygame.mouse.get_pos()
            virtual_mx = mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)
            virtual_my = my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)
            
            center_x = self.x + (self.width / 2)
            center_y = self.y + (self.height / 2)
            
            angle = math.atan2(virtual_my - center_y, virtual_mx - center_x)

            #shot angles
            self.shoot_angle = angle
            self.shoot_x = center_x
            self.shoot_y = center_y
            self.shoot_target_dist = math.hypot(virtual_mx - center_x, virtual_my - center_y)

    def render(self, surface: pygame.Surface) -> None:
        image = settings.TEXTURES['wizard']
        if self.cast_animation_timer > 0:
            frame_idx = self.animations['cast'].get_current_frame()
        else:
            frame_idx = self.current_animation.get_current_frame()
            
        frame_rect = settings.FRAMES['wizard_frames'][frame_idx]
        wizard_surface = image.subsurface(frame_rect)
        
        if not self.facing_right:
            wizard_surface = pygame.transform.flip(wizard_surface, True, False)
            
        surface.blit(wizard_surface, (self.x, self.y))