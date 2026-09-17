import pygame
import random
import math
from gale.state import BaseState
from gale.particle_system import ParticleSystem
from gale.timer import Timer
from gale.input_handler import InputData
from src.entities.DustEffect import DustEffect
from src.entities.player.Player import Player
from src.entities.Projectile import Projectile
from src.entities.CardManager import CardManager
from src.entities.ExpOrb import ExpOrb
from src.entities.Ally import Ally
from src.entities.Totem import Totem
from src.world.waves.WaveManager import WaveManager
from src.world.SwampRoom import SwampRoom
from src.world.InfernoRoom import InfernoRoom
from src.world.CatacombsRoom import CatacombsRoom
from src.world.RockRoom import RockRoom
from src.world.WaterRoom import WaterRoom
from src.world.Pathfinder import Pathfinder

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
    def enter(self, random_mode=False, previous_score=0, previous_kills=None, **kwargs) -> None:
        self.platform_y = 22 
        self.random_mode = random_mode
        
        totem_x = (settings.VIRTUAL_WIDTH // 2) - 19
        wizard_x = settings.VIRTUAL_WIDTH // 2
        
        # Target positions on the ground
        target_totem_y = self.platform_y - 24 
        target_wizard_y = self.platform_y + 11
        
        # START HIGH UP IN THE SKY 
        self.totem = Totem(totem_x, -150)
        self.player = Player(wizard_x, -150)
        
        # NEW INITIAL FADE-IN & DROP EFFECT 
        self.transition_alpha = 255.0
        
        # 1. Fade the screen from black to clear over 1.5 seconds
        Timer.tween(1.5, [(self, {'transition_alpha': 0.0})])
        
        # 2. Drop the characters gently onto the platform
        Timer.tween(1.0, [
            (self.totem, {'y': target_totem_y}),
            (self.player, {'y': target_wizard_y})
        ])

        
        self.kill_counts = previous_kills or {}

        # Cursor
        pygame.mouse.set_visible(False)
        self.cursor_frame = 3

        # Particle
        self.particle_systems = []
        self.player_damage = 5
        self.level_cooldown = 1.0

        #Number for projectiles Player
        self.projectiles = [Projectile() for _ in range(50)]
        #Nuber for projectiles Enemy
        self.enemy_projectiles = [Projectile() for _ in range(30)]


        # Progression system
        if self.random_mode:
            self.current_level = random.randint(1, 40) # Choose a random world
        else:
            self.current_level = 1
        self.load_world()

        self.enemies = []
        # Initialize the manager
        self.wave_manager = WaveManager(self.enemies, self.totem, self.current_room,self.particle_systems)
        self.wave_manager.start_level_sequence(self.current_level)

    
        #Fade-in Fade-out
        self.transition_radius = 350.0

        # LEVEL UP OVERLAY SYSTEM 
        self.card_manager = CardManager()
        self.is_leveling_up = False
        self.active_cards = []
        self.exp_orbs = []

        #Animation Card
        self.is_leveling_up = False
        self.active_cards = []
        self.is_card_animating = False # True blocks clicks during intro/outro
        self.time_scale = 1.0 # 1.0 is normal speed, 0.2 is slow-mo

        #Summon
        self.allies = []
        self.ally_cooldowns = [] # Stores timers for dead allies
        self.summon_mana_cost = 40.0        

        #score
        self.score = previous_score

        

    def load_world(self) -> None:
        """Loads the correct room class based on the global level."""
        if self.current_level <= 8:
            self.current_room = SwampRoom(player=self.player)
        elif self.current_level <= 16:
            self.current_room = InfernoRoom(player=self.player)
        elif self.current_level <= 24:
            self.current_room = CatacombsRoom(player=self.player)
        elif self.current_level <= 32:
            self.current_room = RockRoom(player=self.player)
        else:
            self.current_room = WaterRoom(player=self.player)
        
        # Update the internal density and regenerate
        self._update_room_density()

        # Instantiate the Pathfinder with the newly created room.
        self.pathfinder = Pathfinder(self.current_room)

    def advance_level(self) -> None:
        """Increases the global level and regenerates the map or switches worlds."""

        if getattr(self, 'random_mode', False):
            self.current_level = random.randint(1, 40) # Salta a otro mundo al azar
        else:
            self.current_level += 1

        self.totem.hp = self.totem.max_hp

        # Clean up the previous army before the new drop
        self.allies.clear()
        self.ally_cooldowns.clear()

        # Landing drop effect in the new level
        target_totem_y = self.platform_y - 24 
        target_wizard_y = self.platform_y + 11

        # We "teleport" them to the top of the screen instantly.
        self.totem.y = -150
        self.player.y = -150

        # --- ALPHA FADE-IN ---
        # The screen should be fully black right now from the victory cinematic.
        self.transition_alpha = 255.0

        # And we lower them gently onto their platform in one second.
        Timer.tween(1.0, [
            (self.totem, {'y': target_totem_y}),
            (self.player, {'y': target_wizard_y})
        ])

        # Fade the screen from black (255) to clear (0)
        Timer.tween(1.5, [
            (self, {'transition_alpha': 0.0})
        ])

        # If we hit level 9 or 17, swap the entire world class
        if (self.current_level - 1) % 8 == 0:
            self.load_world()
        else:
            # Otherwise, just make the current world harder and rebuild the blocks
            self._update_room_density()        

        self.wave_manager.current_room = self.current_room
        # Start the next wave of enemies
        self.wave_manager.start_level_sequence(self.current_level)
        

    def _update_room_density(self) -> None:
        """Calculates the internal 1-8 difficulty and forces a map redraw."""
        internal_level = ((self.current_level - 1) % 8) + 1
        self.current_room.current_level = internal_level
        self.current_room._generate_procedural_layout()


    def update(self, dt: float) -> None:
        Timer.update(dt)
        self.player.can_shoot = (len(self.enemies) > 0 and not getattr(self, 'is_transitioning', False)) # We send the Wizard a signal indicating whether or not he can shoot.
    
        # LEVEL UP FREEZE LOGIC 
        if getattr(self, 'is_leveling_up', False):
            pygame.mouse.set_visible(True)
            
            # Get virtual mouse position
            mx, my = pygame.mouse.get_pos()
            virtual_mx = mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)
            virtual_my = my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)
            
            # Update hover states
            for card in self.active_cards:
                card.update(virtual_mx, virtual_my, dt)
                
            # DO NOT update enemies, player, or projectiles while frozen
            return
        
        scaled_dt = dt * getattr(self, 'time_scale', 1.0)

        self.totem.update(scaled_dt)
        self.player.update(scaled_dt)
        self.current_room.update(scaled_dt)

        # UPDATE EXP ORBS
        totem_center_x = self.totem.x + (self.totem.width / 2)
        totem_center_y = self.totem.y + (self.totem.height / 2)

        for orb in reversed(self.exp_orbs):
            orb.update(scaled_dt, totem_center_x, totem_center_y)

            # Check collision with Totem center
            dist = math.hypot(totem_center_x - orb.x, totem_center_y - orb.y)
            if dist < 15: # Collision threshold
                orb.active = False

                # Add XP and check for level up!
                if self.player.add_xp(orb.xp_value):
                        self.is_leveling_up = True
                        self.is_card_animating = True # Block interactions
                        self.active_cards = self.card_manager.get_random_hand(3)
                        
                        # INTRO TWEEN 
                        # Target Y is the center of the screen
                        target_y = (settings.VIRTUAL_HEIGHT / 2) - 54 
                        
                        tweens = []
                        for card in self.active_cards:
                            tweens.append((card, {"y": target_y}))
                            
                        # Animate all cards rising simultaneously with a bouncy effect
                        Timer.tween(0.8, tweens, ease_function_name="out_bounce", 
                                    on_finish=lambda: setattr(self, 'is_card_animating', False))

        # Remove inactive orbs
        self.exp_orbs = [o for o in self.exp_orbs if o.active]


        #Gameover
        # Game Over Cinematic Sequence
        if self.totem.hp <= 0 and not getattr(self, 'is_game_over', False):
            self.is_game_over = True
            self.game_over_timer = 2.5
            
            # We clean up the chaos (We disintegrate the missiles)
            for p in self.enemy_projectiles: p.active = False
            for p in self.projectiles: p.active = False
            
            # Massive particle explosion at the Totem
            for _ in range(6): 
                self.particle_systems.append(BloodEffect(self.totem.x + 10, self.totem.y + 20))
                
            # Destruction Animation: The Totem sinks into the ground over 1.5s.
            Timer.tween(1.5, [
                (self.totem, {'y': self.totem.y + 100})
            ])
                
            # Fade OUT to black (255) before changing to GameOverState
            Timer.tween(2.0, [
                (self, {'transition_alpha': 255.0})
            ])

        # TIME FREEZE
        if getattr(self, 'is_game_over', False):
            self.game_over_timer -= scaled_dt
            
            # We only allow the particles to update for the visual effect.
            for i in range(len(self.particle_systems) - 1, -1, -1):
                self.particle_systems[i].update(scaled_dt)
                if not self.particle_systems[i].active:
                    self.particle_systems.pop(i)
                    
            # When the timer finishes, we perform the state change.
            if self.game_over_timer <= 0:
                pygame.mouse.set_visible(True)
                self.state_machine.change('game_over', kill_counts=self.kill_counts, final_score=self.score)
            return

        #Hit
        if self.totem.hit_flash_timer > 0:
            self.player.hit_flash_timer = self.totem.hit_flash_timer


        if self.level_cooldown > 0:
            self.level_cooldown -= scaled_dt

        #Particle 
        for i in range(len(self.particle_systems) - 1, -1, -1):
            self.particle_systems[i].update(scaled_dt)
            if not self.particle_systems[i].active:
                self.particle_systems.pop(i)


        # We only allow firing if we are NOT in a cinematic.
        if not getattr(self, 'is_transitioning', False):
            if len(self.enemies) > 0:
                #Cursor and shot
                if self.player.just_fired:
                    self.cursor_frame = 4 #Normal shot
                    
                    #Shot
                    for p in self.projectiles:
                        if not p.active:
                            p.fire(self.player.shoot_x, self.player.shoot_y, self.player.shoot_angle, self.player.shoot_target_dist, self.player.projectile_config)
                            p.source_ally = None 
                            break
                else:
                    if self.player.is_exhausted:
                        self.cursor_frame = 6 # NO MANA
                    elif self.player.mana <= self.player.mana_cost * 4:
                        self.cursor_frame = 5 # Gray
                    else:
                        self.cursor_frame = 3 # Blue
            else:
                self.player.just_fired = False
                self.cursor_frame = 3 # Blue
            
        #Block logic
        solid_rects = self.current_room.get_solid_rects()

        for p in self.projectiles:
            if p.active:
                p.update(scaled_dt)
                if not p.is_exploding:
                    if p.get_collision_rect().collidelist(solid_rects) != -1:
                        p.explode()

        # Update the wave manager (spawns enemies automatically)
        self.wave_manager.update(scaled_dt)

        # Colision logic for enemies
        for i in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[i]

          # --- INSTA-KILL ZONE (FAILSAFE) ---
            if not getattr(enemy, 'is_spawning', False):
                # Calculate the exact pixel borders of the procedural map
                map_left = settings.MAP_RENDER_OFFSET_X
                map_right = settings.MAP_RENDER_OFFSET_X + (settings.MAP_WIDTH * settings.TILE_SIZE)
                map_top = settings.MAP_RENDER_OFFSET_Y
                map_bottom = settings.MAP_RENDER_OFFSET_Y + (settings.MAP_HEIGHT * settings.TILE_SIZE_Y)
                
                # We use the center of the enemy to be precise
                cx = enemy.x + (enemy.width / 2)
                cy = enemy.y + (enemy.height / 2)
                
                # If they glitch into the outer black void or deep into the border walls...
                if cx < map_left or cx > map_right or cy < map_top or cy > map_bottom:
                    self.enemies.pop(i) # Silent execution
                    self.wave_manager.enemies_to_spawn += 1 # Refund the spawn ticket
                    continue
            
            if enemy.is_dead:
                tex_id = getattr(enemy, 'texture_id', 'goblin')
                self.kill_counts[tex_id] = self.kill_counts.get(tex_id, 0) + 1
                self.enemies.pop(i)
                continue
            enemy.solid_rects = solid_rects
            enemy.pathfinder = self.pathfinder
            enemy.update(scaled_dt)

            if getattr(enemy, 'block_to_break', None) is not None:
                col, row = enemy.block_to_break
                self.current_room.break_block_at(col, row)
                enemy.block_to_break = None # Clean up the signal

                # Calculate block position to generate dust/debris
                px = settings.MAP_RENDER_OFFSET_X + col * settings.TILE_SIZE + (settings.TILE_SIZE // 2)
                py = settings.MAP_RENDER_OFFSET_Y + row * settings.TILE_SIZE_Y + (settings.TILE_SIZE_Y // 2)
                self.particle_systems.append(BloodEffect(px, py))
              
            best_target = self.totem
            # Check if this enemy was provoked by an ally
            if hasattr(enemy, 'aggro_target') and enemy.aggro_target is not None:
                if not getattr(enemy.aggro_target, 'is_dead', False):
                    # Ally is alive, seek revenge!
                    best_target = enemy.aggro_target
                else:
                    # The ally died, forgive and return to attacking the Totem
                    enemy.aggro_target = None
            enemy.target = best_target
            
            enemy.solid_rects = solid_rects 

            
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)

            #Shoot check
            for p in self.projectiles:
                if p.active and not p.is_exploding:
                    p_rect = pygame.Rect(p.x - 5, p.y - 5, 10, 10)
                    
                    if enemy_rect.colliderect(p_rect) and not getattr(enemy, 'is_spawning', False):
                        p.explode()
                        enemy.take_damage(self.player_damage)
                        self.particle_systems.append(BloodEffect(enemy.x + (enemy.width / 2), enemy.y + (enemy.height / 2)))

                        # If hit by an ally's arrow, get mad at them!
                        if hasattr(p, 'source_ally') and p.source_ally is not None:
                            enemy.aggro_target = p.source_ally

                        # XP REWARD ON DEATH 
                        if enemy.hp <= 0:
                            if getattr(self, 'random_mode', False):
                                self.score += 100  # Fixed points for fairness in the Global Top
                            else:
                                self.score += (10 * self.current_level)

                            #Logic for xp 
                            xp_reward = random.randint(1000, 2000) * self.current_level
                            self.exp_orbs.append(ExpOrb(enemy.x, enemy.y, xp_reward))


            # Ranged enemy attack logic
            if getattr(enemy, 'just_fired', False):
                enemy.just_fired = False 
                for p in self.enemy_projectiles:
                    if not p.active:
                        # Fetch the custom config from the enemy class
                        # Provide a safe default just in case it's missing
                        fallback_config = {'speed': 120, 'texture': 'arrow', 'frames': [0,1,2,3,4,5]}
                        config = getattr(enemy, 'projectile_config', fallback_config)
                        
                        p.fire(enemy.shoot_x, enemy.shoot_y, enemy.shoot_angle, 9999, config)
                        break
        
        # Update arrows goblin
        totem_rect = pygame.Rect(self.totem.x, self.totem.y, self.totem.width, self.totem.height)

        for p in self.enemy_projectiles:
            if p.active:
                p.update(scaled_dt)
                if not p.is_exploding:
                    p_rect = pygame.Rect(p.x - 5, p.y - 5, 10, 10)
                    
                    # Check collision with Totem
                    if totem_rect.colliderect(p_rect):
                        p.explode(texture_id='sparkle', frames=[0, 1, 2, 3]) 
                        self.totem.take_damage(1)
                        continue
                        
                    # Check collision with Allies
                    hit_ally = False
                    for ally in getattr(self, 'allies', []):
                        if not ally.is_dead:
                            ally_rect = pygame.Rect(ally.x, ally.y, ally.width, ally.height)
                            if ally_rect.colliderect(p_rect):
                                p.explode(texture_id='sparkle', frames=[0, 1, 2, 3])
                                ally.take_damage(1) # Enemy arrow damage
                                hit_ally = True
                                self.particle_systems.append(BloodEffect(ally.x + (ally.width / 2), ally.y + (ally.height / 2)))
                                break 
                                
                    if hit_ally:
                        continue

                    # Check collision with Walls
                    if p.get_collision_rect().collidelist(solid_rects) != -1:
                        p.explode(texture_id='sparkle', frames=[0, 1, 2, 3])

        if not self.wave_manager.is_active and len(self.enemies) == 0 and len(self.exp_orbs) == 0 and not getattr(self, 'is_leveling_up', False) and not getattr(self, 'is_card_animating', False):

            # We detect the moment they win in order to trigger the cinematic sequence.
            if not getattr(self, 'is_transitioning', False):
                self.is_transitioning = True
                self.level_cooldown = 2.5

                # Clear projectiles IMMEDIATELY upon winning
                for p in self.enemy_projectiles:
                    p.active = False
                for p in self.projectiles:
                    p.active = False

                # Liftoff: We move both objects off-screen (Y = -100) over 1.5 seconds.
                Timer.tween(2.0, [
                    (self.totem, {'y': -100}),
                    (self.player, {'y': -100})
                ])
                
                # --- FIX: Changed transition_radius to transition_alpha ---
                Timer.tween(2.5, [
                    (self, {'transition_alpha': 255.0})
                ])

            # Once the cooldown ends and the characters are no longer visible, we switch maps.
            if self.level_cooldown <= 0:
                if self.current_level > 39:
                    pygame.mouse.set_visible(True)
                    self.state_machine.change('victory', kill_counts=self.kill_counts, final_score=self.score)

                else:
                    self.advance_level()
                    print(f"Level completed! Advancing to level: {self.current_level}")
                    self.is_transitioning = False
        
        # Update cooldown timers for dead allies
        for i in range(len(self.allies) - 1, -1, -1):
            ally = self.allies[i]
            ally.update(scaled_dt, self.enemies, self.totem, self.allies, solid_rects)
            
            if ally.is_dead:
                self.ally_cooldowns.append(15.0) 
                self.allies.pop(i)
                continue
                
            # Intercept Ranged Attacks
            if getattr(ally.visuals, 'just_fired', False):
                ally.visuals.just_fired = False 
                # Use friendly projectiles so they hurt enemies!
                for p in self.projectiles:
                    if not p.active:
                        fallback = {'speed': 150, 'texture': 'arrow', 'frames': [0,1,2,3,4,5]}
                        config = getattr(ally.visuals, 'projectile_config', fallback)
                        p.fire(ally.visuals.shoot_x, ally.visuals.shoot_y, ally.visuals.shoot_angle, 9999, config)
                        p.source_ally = ally 
                        break

        # Check if we can summon automatically
        active_allies = len(getattr(self, 'allies', []))
        recovering_slots = len(getattr(self, 'ally_cooldowns', []))
        
        # Use getattr to prevent crashes if the player hasn't unlocked the stat yet
        max_summons = getattr(self.player, 'max_summons', 0)
        available_slots = max_summons - active_allies - recovering_slots
        
        if not hasattr(self, 'summon_mana_cost'):
            self.summon_mana_cost = 40.0
        
        if available_slots > 0 and self.player.mana >= self.summon_mana_cost:
            self.player.mana -= self.summon_mana_cost
            
            EnemyClass = random.choice(self.current_room.allowed_enemies)
            
            offset_x = random.choice([-30, self.totem.width + 30])
            spawn_x = self.totem.x + offset_x
            
            enemy_template = EnemyClass(spawn_x, self.totem.y)
            
            new_ally = Ally(spawn_x, self.totem.y, enemy_template, getattr(self.player, 'ally_bonus_damage', 0))
            target_y = self.totem.y
            new_ally.visuals.y = target_y - 200
            new_ally.visuals.is_spawning = True

            def on_ally_drop_finish(ally_obj=new_ally):
                ally_obj.visuals.is_spawning = False
                dust_x = ally_obj.x + (ally_obj.width / 2)
                dust_y = ally_obj.y + ally_obj.height
                self.particle_systems.append(DustEffect(dust_x, dust_y))
            
            Timer.tween(0.8, [(new_ally.visuals, {"y": target_y})], ease_function_name="out_bounce", on_finish=on_ally_drop_finish)
            self.allies.append(new_ally)

        for i in range(len(self.ally_cooldowns) - 1, -1, -1):
            self.ally_cooldowns[i] -= scaled_dt
            if self.ally_cooldowns[i] <= 0:
                self.ally_cooldowns.pop(i)
        
                

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45)) 
        
        stairs_img = settings.TEXTURES['stairs']
        scaled_stairs = pygame.transform.scale(stairs_img, (settings.VIRTUAL_WIDTH, stairs_img.get_height()))
        surface.blit(scaled_stairs, (0, self.platform_y))

        if self.current_room:
            self.current_room.render(surface)

        # Render totem
        self.totem.render(surface)

        #Render enemy
        for enemy in self.enemies:
            enemy.render(surface)

        #Render Ally
        for ally in getattr(self, 'allies', []):
            ally.render(surface)


        #Render player
        self.player.render(surface)

        # RENDER MANA 
        bar_width = 30
        bar_height = 4
        bar_x = self.player.x + (self.player.width / 2) - (bar_width / 2)
        bar_y = self.player.y + self.player.height + 4
        mana_ratio = self.player.mana / self.player.max_mana
        current_bar_width = max(0, int(bar_width * mana_ratio))
        pygame.draw.rect(surface, (20, 20, 30), (bar_x, bar_y, bar_width, bar_height))
        if current_bar_width > 0:
            pygame.draw.rect(surface, (80, 150, 220), (bar_x, bar_y, current_bar_width, bar_height))

        #Render shot
        for p in self.projectiles:
            p.render(surface)

        # Render Particle
        for ps in self.particle_systems:
            ps.render(surface)

        # Render EXP orb
        for ps in self.exp_orbs:
            ps.render(surface)

        # Render arrow goblin
        for p in self.enemy_projectiles:
            p.render(surface)

        #Render heal
        heart_img = settings.TEXTURES['heart']
        full_heart = heart_img.subsurface(settings.FRAMES['heart_frames'][0])
        empty_heart = heart_img.subsurface(settings.FRAMES['heart_frames'][2])
        scale_mult = 2
        new_width = full_heart.get_width() * scale_mult
        new_height = full_heart.get_height() * scale_mult
        
        full_heart = pygame.transform.scale(full_heart, (new_width, new_height))
        empty_heart = pygame.transform.scale(empty_heart, (new_width, new_height))
        
        for i in range(self.totem.max_hp):
            hx = 10 + (i * (new_width + 4))
            hy = 10
            if i < self.totem.hp:
                surface.blit(full_heart, (hx, hy))
            else:
                surface.blit(empty_heart, (hx, hy))

        font = settings.FONTS['small']

        # --- NUEVO: Lógica visual para el modo infinito ---
        if getattr(self, 'random_mode', False):
            level_str = "Level: INF"
        else:
            level_str = f"Level: {self.current_level}"

        # Render the text into a surface (Text, Antialiasing, Color RGB)
        level_text = font.render(level_str, True, (255, 255, 255))
        
        # Position X aligns with the first heart, Position Y goes below the hearts + 8 pixels of padding
        text_x = 10
        text_y = 10 + new_height + 8 
        surface.blit(level_text, (text_x, text_y))



        # --- MODO DEBUG: Dibujar los rectángulos de colisión en rojo ---
        for rect in self.current_room.get_solid_rects():
            pygame.draw.rect(surface, (255, 0, 0), rect, 1)


        # RENDER XP BAR 
        xp_frame_img = settings.TEXTURES['xp_frame']
        xp_fill_img = settings.TEXTURES['xp_fill']
        padding = 10
        bar_x = settings.VIRTUAL_WIDTH - xp_frame_img.get_width() - padding
        bar_y = padding
        
        # Calculate the ratio of current XP to Next Level XP
        xp_ratio = self.player.current_xp / self.player.xp_to_next_level
        
        # Calculate how many pixels wide the blue fill should be
        max_fill_width = xp_fill_img.get_width()
        current_fill_width = max(1, int(max_fill_width * xp_ratio))
        
        # Draw the empty frame first
        surface.blit(xp_frame_img, (bar_x, bar_y))
        
        # Crop the blue fill dynamically based on XP ratio
        if self.player.current_xp > 0:
            fill_rect = pygame.Rect(0, 0, current_fill_width, xp_fill_img.get_height())
            dynamic_fill_surface = xp_fill_img.subsurface(fill_rect)
            
            # Blit the fill inside the frame 
            surface.blit(dynamic_fill_surface, (bar_x + 2, bar_y + 9))

        # RENDER LEVEL UP OVERLAY
        if getattr(self, 'is_leveling_up', False):
            # Draw a dark semi-transparent overlay
            overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))
            
            # Render all 3 cards on top
            for card in self.active_cards:
                card.render(surface)
        
        else: 
            # Cursor
            mx, my = pygame.mouse.get_pos()
            virtual_mx = mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)
            virtual_my = my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)
            cursor_img = settings.TEXTURES['cursor']
            frame_rect = settings.FRAMES['cursor_frames'][self.cursor_frame]
            cursor_surf = cursor_img.subsurface(frame_rect)
            surface.blit(cursor_surf, (virtual_mx - (frame_rect.width / 2), virtual_my - (frame_rect.height / 2)))

         # Cinematic Effect (Iris Wipe)
        if hasattr(self, 'transition_alpha') and self.transition_alpha > 0:
            fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            fade_surface.fill((0, 0, 0))
            # Clamp alpha to max 255 to prevent Pygame crash during tweens
            fade_surface.set_alpha(max(0, min(255, int(self.transition_alpha))))
            surface.blit(fade_surface, (0, 0))
        
    def on_input(self, input_id: str, input_data: InputData) -> None:

        #  CLICK LOGIC FOR CARDS 
        if self.is_leveling_up and not getattr(self, 'is_card_animating', False):
            if input_id == 'click' and input_data.pressed:
                for card in self.active_cards:
                    if card.is_hovered:
                        # Lock everything
                        self.is_card_animating = True
                        for c in self.active_cards:
                            c.locked = True
                        
                        # OUTRO TWEEN 
                        center_x = (settings.VIRTUAL_WIDTH / 2) - (card.width / 2)
                        center_y = (settings.VIRTUAL_HEIGHT / 2) - (card.height / 2)
                        
                        tweens = []
                        for c in self.active_cards:
                            if c == card:
                                # Selected card zooms in and goes to center
                                tweens.append((c, {"x": center_x, "y": center_y, "scale": 1.5}))
                            else:
                                # Unselected cards fall off screen
                                tweens.append((c, {"y": settings.VIRTUAL_HEIGHT + 150}))
                        
                        # What happens when the outro animation finishes:
                        def finish_outro():
                            card.apply_effect(self.player, self)
                            self.is_leveling_up = False
                            self.is_card_animating = False
                            self.active_cards.clear()
                            pygame.mouse.set_visible(False)
                            
                            #  SLOW MOTION EFFECT 
                            self.time_scale = 0.2 # Enter The Matrix
                            Timer.tween(1.5, [(self, {"time_scale": 1.0})], ease_function_name="in_out_cubic")
                            
                        # Start the outro animation
                        Timer.tween(0.6, tweens, ease_function_name="out_cubic", on_finish=finish_outro)
                        break

        if input_id == 'quit' and input_data.pressed:
            pygame.mouse.set_visible(True)
            self.state_machine.change('main_menu')

        if input_id == 'confirm' and input_data.pressed:
            if self.level_cooldown <= 0:
                self.advance_level()
                print(f"Level advanced to: {self.current_level}")
                self.level_cooldown = 0.3