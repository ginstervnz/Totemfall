import pygame
import random
import math
from gale.state import BaseState
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
from src.entities.Effects import BloodEffect, DarkSmokeEffect, LightningEffect
from src.ui.HUD import HUD

import settings

class PlayState(BaseState):
    def enter(self, random_mode=False, previous_score=0, previous_kills=None, saved_player=None, **kwargs) -> None:
        self.platform_y = 22 
        self.random_mode = random_mode
        
        totem_x = (settings.VIRTUAL_WIDTH // 2) - 19
        wizard_x = settings.VIRTUAL_WIDTH // 2
        
        # Target positions on the ground
        target_totem_y = self.platform_y - 24 
        target_wizard_y = self.platform_y + 11
        
        # START HIGH UP IN THE SKY 
        self.totem = Totem(totem_x, -150)

        if saved_player is not None:
            # If we're coming from Story Mode, we use the super-powerful wizard.
            self.player = saved_player
            # We teleport him to the sky for the falling animation.
            self.player.x = wizard_x
            self.player.y = -150
        else:
            # Si venimos del menú principal, creamos un mago nivel 1
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
            settings.AUDIO_MANAGER.fade_out_and_play('assets/sounds/level_music/swamp_music.mp3')
        elif self.current_level <= 16:
            self.current_room = InfernoRoom(player=self.player)
            settings.AUDIO_MANAGER.fade_out_and_play('assets/sounds/level_music/inferno_music.mp3')
        elif self.current_level <= 24:
            self.current_room = CatacombsRoom(player=self.player)
            settings.AUDIO_MANAGER.fade_out_and_play('assets/sounds/level_music/catacombs_music.mp3')
        elif self.current_level <= 32:
            self.current_room = RockRoom(player=self.player)
            settings.AUDIO_MANAGER.fade_out_and_play('assets/sounds/level_music/rockroom_music.mp3')
        else:
            self.current_room = WaterRoom(player=self.player)
            settings.AUDIO_MANAGER.fade_out_and_play('assets/sounds/level_music/wateroom_music.mp3')
        
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
        self.player.mana = self.player.max_manac

        #  RESET SHIELD FOR NEXT LEVEL 
        if getattr(self.totem, 'has_shield_ability', False):
            self.totem.reset_shield()

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
        self.player.can_shoot = (len(self.enemies) > 0 and 
                                 not getattr(self, 'is_transitioning', False) and 
                                 not getattr(self, 'is_game_over', False))
    
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

        #  QUEUE SYSTEM FOR LEVEL UPS
        # 1. Store the level before absorbing any orbs in this frame
        previous_level = self.player.level

        for orb in reversed(self.exp_orbs):
            orb.update(scaled_dt, totem_center_x, totem_center_y)

            # Check collision with Totem center
            dist = math.hypot(totem_center_x - orb.x, totem_center_y - orb.y)
            if dist < 15: # Collision threshold
                orb.active = False
                
                # Just add the XP! We DO NOT trigger the UI here anymore.
                self.player.add_xp(orb.xp_value)
                settings.AUDIO_MANAGER.play_sfx('exp') 
            
        # Remove inactive orbs
        self.exp_orbs = [o for o in self.exp_orbs if o.active]

        # 2. Calculate exactly how many levels were gained
        levels_gained = self.player.level - previous_level
        if levels_gained > 0:
            # Add them to our queue (initialize to 0 if it doesn't exist yet)
            self.pending_level_ups = getattr(self, 'pending_level_ups', 0) + levels_gained

        # 3. If we have pending level ups and the UI is NOT currently active, trigger it!
        if getattr(self, 'pending_level_ups', 0) > 0 and not getattr(self, 'is_leveling_up', False) and not getattr(self, 'is_game_over', False):
            
            # Consume one level up from the queue
            self.pending_level_ups -= 1 
            
            self.is_leveling_up = True
            self.is_card_animating = True # Block interactions
            self.active_cards = self.card_manager.get_random_hand(3)
            settings.AUDIO_MANAGER.play_sfx('spawn_card')
            # INTRO TWEEN 
            target_y = (settings.VIRTUAL_HEIGHT / 2) - 54 
            tweens = []
            for card in self.active_cards:
                tweens.append((card, {"y": target_y}))
                
            Timer.tween(0.8, tweens, ease_function_name="out_bounce", 
                        on_finish=lambda: setattr(self, 'is_card_animating', False))

        # Game Over Cinematic Sequence
        if self.totem.hp <= 0 and not getattr(self, 'is_game_over', False):
            self.is_game_over = True
            self.game_over_timer = 3.5 # Time for the shake and smoke to play out
            
            # Cancel level ups and UI
            self.is_leveling_up = False
            self.pending_level_ups = 0
            self.active_cards.clear()
            pygame.mouse.set_visible(False)
            
            # Clean up the chaos (disintegrate enemy missiles)
            for p in self.enemy_projectiles: p.active = False
            for p in self.projectiles: p.active = False
            self.player.cast_animation_timer = 0
            self.player.just_fired = False

            # STOP THE MUSIC 
            settings.AUDIO_MANAGER.stop_music_fade(2.5)
            #  TRIGGER THE SHAKE (Violent vibration for 2.5 seconds)
            self.totem.shake_timer = 2.5
            settings.AUDIO_MANAGER.play_sfx('totemfall')
            #  CONTINUOUS SMOKE ERUPTION
            # Spawns dark smoke repeatedly from the Totem's core
            Timer.every(0.1, lambda: self.particle_systems.append(DarkSmokeEffect(self.totem.x + 19, self.totem.y + 24)), limit=25)
            
            #  FADE OUT TO BLACK
            # After 2 seconds of shaking, start fading to black over 1.5 seconds
            Timer.after(3.0, lambda: Timer.tween(1.5, [(self, {'transition_alpha': 255.0})]))
        
        # TIME FREEZE
        if getattr(self, 'is_game_over', False):
            self.game_over_timer -= scaled_dt
            self.totem.update(scaled_dt)
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
                            config = self.player.projectile_config.copy()
                            if getattr(self.player, 'shoot_is_electric', False):
                                config['is_electric'] = True
                            p.fire(self.player.shoot_x, self.player.shoot_y, self.player.shoot_angle, self.player.shoot_target_dist, config)
                            p.source_ally = None 
                            settings.AUDIO_MANAGER.play_sfx('shoot_wizard')
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
            
        # --- PROJECTILE VS WALL COLLISION ---
        solid_rects = self.current_room.get_solid_rects()

        for p in self.projectiles:
            if p.active:
                p.update(scaled_dt)
                
                if not getattr(p, 'is_exploding', False):
                    
                    # Get the exact index of the wall we hit
                    hit_index = p.get_collision_rect().collidelist(solid_rects)
                    
                    if hit_index != -1:
                        can_destroy = getattr(self.player, 'can_destroy_blocks', False)
                        
                        if can_destroy:
                            # 1. Get the EXACT rectangle of the wall we hit
                            hit_rect = solid_rects[hit_index]
                            
                            # 2. Convert the WALL's position to grid coordinates 
                            col = int((hit_rect.x - settings.MAP_RENDER_OFFSET_X) // settings.TILE_SIZE)
                            row = int((hit_rect.y - settings.MAP_RENDER_OFFSET_Y) // settings.TILE_SIZE_Y)
                            
                            # 3. Apply the strict bounds (just like the BaseEnemy logic)
                            if 0 <= col < settings.MAP_WIDTH and 0 <= row < settings.MAP_HEIGHT:
                                
                                # RESTRICTION 1: Bottom edge
                                if row < settings.MAP_HEIGHT - 1:
                                    
                                    # RESTRICTION 2: Side edges
                                    if col > 0 and col < settings.MAP_WIDTH - 1:
                                        
                                        # RESTRICTION 3: Overhead protective roof
                                        if row > 3:
                                            # If it passes all tests, destroy the block!
                                            self.current_room.break_block_at(col, row)
                                                
                        # The projectile always explodes upon hitting a wall
                        settings.AUDIO_MANAGER.play_sfx('hit_wall')
                        p.explode()
                        if getattr(p, 'is_electric', False):
                            self._trigger_chain_lightning(p.x, p.y)

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
                
                grace_margin = 32
                if (cx < map_left - grace_margin or cx > map_right + grace_margin or 
                    cy < map_top - grace_margin or cy > map_bottom + grace_margin):
                    
                    self.enemies.pop(i) 
                    self.wave_manager.enemies_to_spawn += 1 
                    continue
            
            if enemy.is_dead:
                tex_id = getattr(enemy, 'texture_id', 'goblin')
                self.kill_counts[tex_id] = self.kill_counts.get(tex_id, 0) + 1
                self.enemies.pop(i)
                settings.AUDIO_MANAGER.play_sfx('dead_enemy')
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
                        
                        #  UNIFIED PROJECTILE DAMAGE 
                        # If the arrow came from an ally, use their specific damage
                        if hasattr(p, 'source_ally') and p.source_ally is not None:
                            actual_damage = getattr(p.source_ally.visuals, 'damage', 1)
                            enemy.aggro_target = p.source_ally
                        else:
                            # If it came from the main player, use the player's massive damage
                            actual_damage = self.player_damage
                            
                        enemy.take_damage(actual_damage)
                        
                        self.particle_systems.append(BloodEffect(enemy.x + (enemy.width / 2), enemy.y + (enemy.height / 2)))
                        settings.AUDIO_MANAGER.play_sfx('hit_enemy')

                        # XP REWARD ON DEATH 
                        if enemy.hp <= 0:
                            if getattr(self, 'random_mode', False):
                                self.score += 100  # Fixed points for fairness in the Global Top
                            else:
                                self.score += (10 * self.current_level)

                            #Logic for xp 
                            xp_reward = random.randint(10, 100) * self.current_level
                            self.exp_orbs.append(ExpOrb(enemy.x, enemy.y, xp_reward))
                        
                        # CHAIN LIGHTNING FROM ENEMY 
                        if getattr(p, 'is_electric', False):
                            # Cast the ray from the center of the hit enemy
                            self._trigger_chain_lightning(enemy.x + (enemy.width/2), enemy.y + (enemy.height/2))


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
                        settings.AUDIO_MANAGER.play_sfx('shoot_enemy')
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
                        settings.AUDIO_MANAGER.play_sfx('hit_totem')
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
                        settings.AUDIO_MANAGER.play_sfx('hit_wall')

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
                    self.state_machine.change('victory', kill_counts=self.kill_counts, final_score=self.score, saved_player=self.player)

                else:
                    self.advance_level()
                    # DEBUG: Level print(f"Level completed! Advancing to level: {self.current_level}")
                    self.is_transitioning = False
        
        # Update cooldown timers for dead allies
        for i in range(len(self.allies) - 1, -1, -1):
            ally = self.allies[i]
            ally.update(scaled_dt, self.enemies, self.totem, self.allies, solid_rects)
            
            if ally.is_dead:
                self.ally_cooldowns.append(15.0) 
                self.allies.pop(i)
                settings.AUDIO_MANAGER.play_sfx('dead_ally')
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
                settings.AUDIO_MANAGER.play_sfx('spawn_ally')
            
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


        # DEBUG:Collision red block
        #for rect in self.current_room.get_solid_rects():
            #pygame.draw.rect(surface, (255, 0, 0), rect, 1)

        # We delegate all static drawing to the optimized HUD.
        if not getattr(self, 'is_leveling_up', False):
            HUD.render(surface, self.player, self.totem, self.current_level, getattr(self, 'random_mode', False), self.cursor_frame)
        else:
            # If we are leveling up, we draw the overlay and the cards.
            overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))
            for card in self.active_cards: 
                card.render(surface)

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
                        settings.AUDIO_MANAGER.play_sfx('confirm')
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
                # DEBUG: Level print(f"Level advanced to: {self.current_level}")
                self.level_cooldown = 0.3

    def _trigger_chain_lightning(self, start_x: float, start_y: float) -> None:
        # Play the electric impact sound
        if 'electro_fire' in getattr(settings, 'AUDIO_MANAGER').sounds:
            settings.AUDIO_MANAGER.play_sfx('electro_fire')
            
        distances = []
        for enemy in self.enemies:
            # Only target enemies that are fully spawned and currently alive
            if not getattr(enemy, 'is_spawning', False) and not getattr(enemy, 'is_dead', False) and enemy.hp > 0:
                ex = enemy.x + (enemy.width / 2)
                ey = enemy.y + (enemy.height / 2)
                dist = math.hypot(ex - start_x, ey - start_y)
                distances.append((dist, enemy, ex, ey))
                
        # Sort enemies by proximity (closest first)
        distances.sort(key=lambda item: item[0])
        
        # Chain jumps to a maximum of 2 targets
        targets = distances[:2]
        lightning_damage = getattr(self.player, 'lightning_damage', 4.0)
        
        for dist, target_enemy, ex, ey in targets:
            # 1. Render the electric arc connecting the points
            self.particle_systems.append(LightningEffect(start_x, start_y, ex, ey))
            
            # 2. Apply damage and physical blood feedback
            target_enemy.take_damage(lightning_damage)
            self.particle_systems.append(BloodEffect(ex, ey))
            
            # 3. Handle kills caused specifically by the chain lightning
            if target_enemy.hp <= 0:
                if getattr(self, 'random_mode', False):
                    self.score += 100
                else:
                    self.score += (10 * self.current_level)
                xp_reward = random.randint(10, 100) * self.current_level
                self.exp_orbs.append(ExpOrb(target_enemy.x, target_enemy.y, xp_reward))