import math
import pygame
from src.entities.BaseEntityState import BaseEntityState

class EnemyRangedWalkState(BaseEntityState):
    def enter(self) -> None:
        self.entity.current_animation = self.entity.animations['walk']

    def update(self, dt: float) -> None:
        if hasattr(self.entity, 'target'):
            
            center_x = self.entity.x + (self.entity.width / 2)
            center_y = self.entity.y + (self.entity.height / 2)
            target_center_x = self.entity.target.x + (self.entity.target.width / 2)
            target_center_y = self.entity.target.y + (self.entity.target.height / 2)
            
           
            dist_x = target_center_x - center_x
            dist_y = target_center_y - center_y
            distance = math.hypot(dist_x, dist_y)
            
            
            if hasattr(self.entity, 'attack_range') and distance <= self.entity.attack_range:
                if 'attack' in self.entity.state_machine.states:
                    self.entity.state_machine.change('attack')
            else:
                center_x = self.entity.x + (self.entity.width / 2)
                target_center_x = self.entity.target.x + (self.entity.target.width / 2)
                dist_x = target_center_x - center_x
                dist_y = (self.entity.target.y + self.entity.target.height - 10) - self.entity.y
                angle = math.atan2(dist_y, dist_x)
                
                dx = math.cos(angle) * self.entity.speed * dt
                self.entity.x += dx
                if hasattr(self.entity, 'solid_rects'):
                    rect = pygame.Rect(self.entity.x, self.entity.y, self.entity.width, self.entity.height)
                    if rect.collidelist(self.entity.solid_rects) != -1:
                        self.entity.x -= dx
                
                dy = math.sin(angle) * self.entity.speed * dt
                self.entity.y += dy
                if hasattr(self.entity, 'solid_rects'):
                    rect = pygame.Rect(self.entity.x, self.entity.y, self.entity.width, self.entity.height)
                    if rect.collidelist(self.entity.solid_rects) != -1:
                        self.entity.y -= dy
        else:
            self.entity.y += self.entity.speed * dt