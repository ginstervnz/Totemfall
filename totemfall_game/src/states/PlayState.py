import pygame
from gale.state import BaseState
from gale.particle_system import ParticleSystem
from gale.input_handler import InputData
from src.entities.player.Player import Player
from src.entities.Projectile import Projectile
from src.entities.Totem import Totem
from src.entities.enemies.monsters.Batilisk import Batilisk
from src.entities.enemies.monsters.Goblin import Goblin

import settings

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



class PlayState(BaseState):
    def enter(self) -> None:
        self.platform_y = 22 
        totem_x = (settings.VIRTUAL_WIDTH // 2) - 19
        totem_y = self.platform_y - 24 
        self.totem = Totem(totem_x, totem_y)
        wizard_x = settings.VIRTUAL_WIDTH // 2
        wizard_y = self.platform_y + 11
        self.player = Player(wizard_x, wizard_y)

        # Cursor
        pygame.mouse.set_visible(False)
        self.cursor_frame = 3

        #Shot player
        self.projectiles = [Projectile() for _ in range(50)]
        
        # Dictionary for magicball
        self.basic_shot_config = {
            'speed': 150,
            'texture': 'magic_bolt',
            'frames': [0, 1, 2, 3]
        }

        # Shot enemy goblins
        self.enemy_projectiles = [Projectile() for _ in range(30)]

        self.arrow_config = {
            'speed': 120,
            'texture': 'arrow',
            'frames': [0,1,2,3,4,5] 
        }


        # --- ENTORNO DE PRUEBAS ---
        test_enemy = Goblin(settings.VIRTUAL_WIDTH // 2 - 10, 150)
        test_enemy.target = self.totem
        test_enemy.target_y = self.platform_y + 50
        self.enemies = [test_enemy]


        #Don't erase
        self.particle_systems = []
        self.player_damage = 5


    def update(self, dt: float) -> None:
        self.totem.update(dt)
        self.player.update(dt)

        #Particle 
        for i in range(len(self.particle_systems) - 1, -1, -1):
            self.particle_systems[i].update(dt)
            if not self.particle_systems[i].active:
                self.particle_systems.pop(i)



        #Cursor and shot
        if self.player.just_fired:
            #Cursor
            self.cursor_frame = 4

            #Shot
            for p in self.projectiles:
                if not p.active:
                    # Create magic ball
                    p.fire(self.player.shoot_x, self.player.shoot_y, self.player.shoot_angle, self.player.shoot_target_dist, self.basic_shot_config)
                    break
        else:
            self.cursor_frame = 3
        for p in self.projectiles:
            p.update(dt)

        # Colision logic for enemies
        for i in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[i]
            
            if enemy.is_dead:
                self.enemies.pop(i)
                continue
                
            enemy.update(dt)
            
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            
            for p in self.projectiles:
                if p.active and not p.is_exploding:
                    p_rect = pygame.Rect(p.x - 5, p.y - 5, 10, 10)
                    
                    if enemy_rect.colliderect(p_rect):
                        p.explode()
                        enemy.take_damage(self.player_damage)
                        self.particle_systems.append(BloodEffect(enemy.x + (enemy.width / 2), enemy.y + (enemy.height / 2)))

            #Goblin attack
            if getattr(enemy, 'just_fired', False):
                enemy.just_fired = False 
                for p in self.enemy_projectiles:
                    if not p.active:
                        p.fire(enemy.shoot_x, enemy.shoot_y, enemy.shoot_angle, 9999, self.arrow_config)
                        break
        
        # Update arrows goblin
        for p in self.enemy_projectiles:
            p.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45)) 
        
        stairs_img = settings.TEXTURES['stairs']
        scaled_stairs = pygame.transform.scale(stairs_img, (settings.VIRTUAL_WIDTH, stairs_img.get_height()))
        surface.blit(scaled_stairs, (0, self.platform_y))

        # Render totem
        self.totem.render(surface)

        #Render enemy
        for enemy in self.enemies:
            enemy.render(surface)

        #Render player
        self.player.render(surface)

        #Render shot
        for p in self.projectiles:
            p.render(surface)

        # Render Particle
        for ps in self.particle_systems:
            ps.render(surface)

        # Render arrow goblin
        for p in self.enemy_projectiles:
            p.render(surface)

        #Cursor
        mx, my = pygame.mouse.get_pos()
        virtual_mx = mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)
        virtual_my = my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)
        cursor_img = settings.TEXTURES['cursor']
        frame_rect = settings.FRAMES['cursor_frames'][self.cursor_frame]
        cursor_surf = cursor_img.subsurface(frame_rect)
        surface.blit(cursor_surf, (virtual_mx - (frame_rect.width / 2), virtual_my - (frame_rect.height / 2)))

        
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == 'quit' and input_data.pressed:
            pygame.mouse.set_visible(True)
            self.state_machine.change('main_menu')