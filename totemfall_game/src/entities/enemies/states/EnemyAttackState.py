import pygame
import math
from src.entities.BaseEntityState import BaseEntityState
from gale.animation import Animation
import settings

class EnemyAttackState(BaseEntityState):
    def enter(self) -> None:
        self.entity.current_animation = self.entity.animations.get('idle', self.entity.animations['walk'])
        self.attack_rate = 1.0
        self.timer = self.attack_rate
        self.swing_animation = Animation([0, 1, 2, 3], 0.05) 
        self.is_swinging = False
        self.has_damaged = False

        self.texture_id = getattr(self.entity, 'attack_texture', 'attack_swing')
        self.frame_list = getattr(self.entity, 'attack_frames', [0, 1, 2, 3])
        self.damage_frame = getattr(self.entity, 'attack_damage_frame', 2)


    def update(self, dt: float) -> None:
        self.timer -= dt
        
        if self.is_swinging:
            self.swing_animation.update(dt)
            frame_idx = self.swing_animation.get_current_frame()
            if frame_idx == self.damage_frame and not self.has_damaged:
                if hasattr(self.entity, 'target'):
                    self.entity.target.take_damage(1)
                self.has_damaged = True

            if frame_idx == 3:
                self.is_swinging = False

        if self.timer <= 0:
            self.timer = self.attack_rate
            self.is_swinging = True
            self.swing_animation = Animation([0, 1, 2, 3], 0.05)
            self.has_damaged = False 

    def render(self, surface: pygame.Surface) -> None:
        if self.is_swinging and hasattr(self.entity, 'target'):
            image = settings.TEXTURES[self.texture_id]
            frame_idx = self.swing_animation.get_current_frame()
            frame_rect = settings.FRAMES[f'{self.texture_id}_frames'][frame_idx]
            
            swing_surface = image.subsurface(frame_rect)
            
            
            enemy_center_x = self.entity.x + (self.entity.width / 2)
            enemy_center_y = self.entity.y + (self.entity.height / 2)
            
            target_center_x = self.entity.target.x + (self.entity.target.width / 2)
            target_center_y = self.entity.target.y + (self.entity.target.height * 0.75) 
            angle_rad = math.atan2(target_center_y - enemy_center_y, target_center_x - enemy_center_x)
            angle_deg = math.degrees(-angle_rad) 
            
            rotated_swing = pygame.transform.rotate(swing_surface, angle_deg)
            
            render_x = enemy_center_x + (math.cos(angle_rad) * 15)
            render_y = enemy_center_y + (math.sin(angle_rad) * 15)
            
            rect = rotated_swing.get_rect(center=(render_x, render_y))
            surface.blit(rotated_swing, rect)