import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from src.entities.player.Player import Player
from src.entities.Projectile import Projectile
from src.entities.Totem import Totem
from src.world.SwampRoom import SwampRoom
from src.world.InfernoRoom import InfernoRoom
from src.world.CatacombsRoom import CatacombsRoom
from src.world.RockRoom import RockRoom
from src.world.WaterRoom import WaterRoom

import settings

class PlayState(BaseState):
    def enter(self) -> None:
        self.platform_y = 22 
        totem_x = (settings.VIRTUAL_WIDTH // 2) - 19
        totem_y = self.platform_y - 24 
        self.totem = Totem(totem_x, totem_y)
        wizard_x = settings.VIRTUAL_WIDTH // 2
        wizard_y = self.platform_y + 11
        self.player = Player(wizard_x, wizard_y)

        # Progression system
        self.current_level = 1
        self.load_world()

        # Cursor
        pygame.mouse.set_visible(False)
        self.cursor_frame = 3

        #Shot
        self.projectiles = [Projectile() for _ in range(50)]
        
        # Dictionary for magicball
        self.basic_shot_config = {
            'speed': 150,
            'texture': 'magic_bolt',
            'frames': [0, 1, 2, 3]
        }
# --- NUEVO: Temporizador anti-rebote (Debounce) ---
        self.level_cooldown = 0

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

    def advance_level(self) -> None:
        """Increases the global level and regenerates the map or switches worlds."""
        self.current_level += 1
        
        # If we hit level 9 or 17, swap the entire world class
        if (self.current_level - 1) % 8 == 0:
            self.load_world()
        else:
            # Otherwise, just make the current world harder and rebuild the blocks
            self._update_room_density()

    def _update_room_density(self) -> None:
        """Calculates the internal 1-8 difficulty and forces a map redraw."""
        internal_level = ((self.current_level - 1) % 8) + 1
        self.current_room.current_level = internal_level
        self.current_room._generate_procedural_layout()

    def update(self, dt: float) -> None:
        self.totem.update(dt)
        self.player.update(dt)
        self.current_room.update(dt)

        # --- NUEVO: Reducir el cooldown con el tiempo Delta ---
        if self.level_cooldown > 0:
            self.level_cooldown -= dt

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

        solid_rects = self.current_room.get_solid_rects()

        for p in self.projectiles:
            if p.active:
                p.update(dt)

                # If the dynamic hitbox collides with a wall in the room, we deactivate the magic.
                if p.get_collision_rect().collidelist(solid_rects) != -1:
                    p.active = False

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 25, 45)) 
        
        stairs_img = settings.TEXTURES['stairs']
        scaled_stairs = pygame.transform.scale(stairs_img, (settings.VIRTUAL_WIDTH, stairs_img.get_height()))
        surface.blit(scaled_stairs, (0, self.platform_y))

        if self.current_room:
            self.current_room.render(surface)

        # Render totem
        self.totem.render(surface)

        #Render player
        self.player.render(surface)

        #Render shot
        for p in self.projectiles:
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

        if input_id == 'confirm' and input_data.pressed:
            if self.level_cooldown <= 0:
                self.advance_level()
                print(f"Level advanced to: {self.current_level}")
                self.level_cooldown = 0.3