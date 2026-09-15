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

        # Mana logic
        self.max_mana = 100.0
        self.mana = self.max_mana
        self.mana_cost = 10.0 
        self.mana_regen = 20.5
        self.is_exhausted = False

        # Summoning stats
        self.max_summons = 0
        self.ally_bonus_damage = 0


        #Shot 
        self.fire_rate = 0.5 
        self.shoot_timer = self.fire_rate
        self.just_fired = False
        self.cast_animation_timer = 0

        self.projectile_config = {
            'speed': 150,
            'texture': 'magic_bolt',
            'frames': [0, 1, 2, 3]
        }

        self.can_shoot = True

        #Heal
        self.max_hp = 5
        self.hp = self.max_hp
        self.hit_flash_timer = 0

        # --- EXPERIENCE SYSTEM ---
        self.level = 1
        self.current_xp = 0
        # Formula: 100 * (Level ^ 1.5)
        self.xp_to_next_level = 100


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

    def add_xp(self, amount: int) -> bool:
        """Adds experience and handles leveling up."""
        self.current_xp += amount
        leveled_up = False
        # While loop in case the player gains enough XP to level up multiple times
        while self.current_xp >= self.xp_to_next_level:
            self.current_xp -= self.xp_to_next_level
            self.level += 1
            
            # Recalculate next level requirement using the exponential formula
            self.xp_to_next_level = int(100 * (self.level ** 1.5))
            
            # Increase max mana on level up
            self.max_mana += 10
            self.mana = self.max_mana
            leveled_up = True
        return leveled_up


    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        self.hit_flash_timer = 0.15

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)
        self.x = max(0, min(self.x, settings.VIRTUAL_WIDTH - self.width))

        self.current_animation.update(dt)
        self.animations['cast'].update(dt)

        # Logic for mana
        if self.mana < self.max_mana:
            self.mana = min(self.max_mana, self.mana + (self.mana_regen * dt))

        # If mana reaches 0 
        if self.mana < self.mana_cost:
            self.is_exhausted = True
        elif self.mana >= self.mana_cost * 4:
            self.is_exhausted = False

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if self.cast_animation_timer > 0:
            self.cast_animation_timer -= dt

        # Shoot
        self.just_fired = False
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and not self.is_exhausted and self.can_shoot:
            self.shoot_timer = self.fire_rate
            self.just_fired = True
            self.mana -= self.mana_cost

            self.cast_animation_timer = 0.15 
            self.animations['cast'] = Animation([4,5], 0.05)
            
            mx, my = pygame.mouse.get_pos()
            virtual_mx = mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)
            virtual_my = my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)
            
            center_x = self.x + (self.width / 2)
            center_y = self.y + (self.height / 2)
            
            angle = math.atan2(virtual_my - center_y, virtual_mx - center_x)

            self.shoot_angle = angle
            self.shoot_x = center_x
            self.shoot_y = center_y
            self.shoot_target_dist = math.hypot(virtual_mx - center_x, virtual_my - center_y)

    def render(self, surface: pygame.Surface) -> None:
        image = settings.TEXTURES['wizard']
        
        if self.hit_flash_timer > 0:
            frame_idx = 6  
        elif self.cast_animation_timer > 0:
            frame_idx = self.animations['cast'].get_current_frame()
        else:
            frame_idx = self.current_animation.get_current_frame()
            
        frame_rect = settings.FRAMES['wizard_frames'][frame_idx]
        
        entity_surface = image.subsurface(frame_rect).copy() 
        
        if not self.facing_right:
            entity_surface = pygame.transform.flip(entity_surface, True, False)
            
        if self.hit_flash_timer > 0:
            entity_surface.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            
        surface.blit(entity_surface, (self.x, self.y))