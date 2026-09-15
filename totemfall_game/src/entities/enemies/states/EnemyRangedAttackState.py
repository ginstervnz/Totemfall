import math
import random
import settings
import pygame
from src.entities.BaseEntityState import BaseEntityState

class EnemyRangedAttackState(BaseEntityState):
    def enter(self) -> None:
        self.entity.current_animation = self.entity.animations.get('walk')
        self.attack_rate = 2.0
        self.timer = self.attack_rate
        self.has_shot = False
        self.shoot_time = 1.0 
        
        self.strafe_dir = random.choice([-1, 1])

    def update(self, dt: float) -> None:
        self.timer -= dt
        
        if self.timer <= self.shoot_time and not self.has_shot:
            self.fire_arrow()
            self.has_shot = True

        is_aiming = (self.shoot_time + 0.2) > self.timer > (self.shoot_time - 0.2)

        if not is_aiming and hasattr(self.entity, 'target'):
            center_x = self.entity.x + (self.entity.width / 2)
            center_y = self.entity.y + (self.entity.height / 2)
            target_center_x = self.entity.target.x + (self.entity.target.width / 2)
            target_center_y = self.entity.target.y + (self.entity.target.height / 2)
            
            distance = math.hypot(target_center_x - center_x, target_center_y - center_y)
            
            if distance > self.entity.attack_range + 10:
                self.entity.state_machine.change('walk')
                return
            
            angle_to_target = math.atan2(target_center_y - center_y, target_center_x - center_x)
            strafe_angle = angle_to_target + (math.pi / 2) * self.strafe_dir
            
            move_speed = self.entity.speed * 0.7 
            dx = math.cos(strafe_angle) * move_speed * dt
            dy = math.sin(strafe_angle) * move_speed * dt
            
            flip = False
            
            # Apply X movement and check screen bounds and wall collisions
            self.entity.x += dx
            if self.entity.x < 10 or self.entity.x > settings.VIRTUAL_WIDTH - (self.entity.width + 10):
                flip = True
                self.entity.x -= dx
            elif hasattr(self.entity, 'solid_rects'):
                rect = pygame.Rect(self.entity.x, self.entity.y, self.entity.width, self.entity.height)
                if rect.collidelist(self.entity.solid_rects) != -1:
                    flip = True
                    self.entity.x -= dx
                    
            # Apply Y movement and check screen bounds and wall collisions
            self.entity.y += dy
            if self.entity.y < 10 or self.entity.y > settings.VIRTUAL_HEIGHT - (self.entity.height + 10):
                flip = True
                self.entity.y -= dy
            elif hasattr(self.entity, 'solid_rects'):
                rect = pygame.Rect(self.entity.x, self.entity.y, self.entity.width, self.entity.height)
                if rect.collidelist(self.entity.solid_rects) != -1:
                    flip = True
                    self.entity.y -= dy
                    
            # Reverse the strafe direction if an obstacle or edge is hit
            if flip:
                self.strafe_dir *= -1

        if self.timer <= 0:
            self.timer = self.attack_rate
            self.has_shot = False
            self.strafe_dir = random.choice([-1, 1])

    def fire_arrow(self) -> None:
        self.entity.just_fired = True
        
        if hasattr(self.entity, 'target'):
            center_x = self.entity.x + (self.entity.width / 2)
            center_y = self.entity.y + (self.entity.height / 2)
            
            target_center_x = self.entity.target.x + (self.entity.target.width / 2)
            target_center_y = self.entity.target.y + (self.entity.target.height / 2)
            
            self.entity.shoot_angle = math.atan2(target_center_y - center_y, target_center_x - center_x)
            
            self.entity.shoot_x = center_x + (math.cos(self.entity.shoot_angle) * 8)
            self.entity.shoot_y = center_y + (math.sin(self.entity.shoot_angle) * 8)