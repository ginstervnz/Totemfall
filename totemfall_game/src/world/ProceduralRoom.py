import random
import pygame
import settings
from src.entities.Prop import Prop

class ProceduralRoom: 
    def __init__(self, player, brick_texture: str, prop_texture: str, max_prop_frame: int) -> None:
        self.player = player
        self.current_level = 1
        self.max_levels = 8
        self.brick_texture = brick_texture
        self.prop_texture = prop_texture
        self.max_prop_frame = max_prop_frame
        
        self.objects = []
        self.entities = []
        
        self._generate_procedural_layout()

    def _generate_procedural_layout(self) -> None:
        self.objects.clear()
        start_row = 4
        grid = [[False for _ in range(settings.MAP_WIDTH)] for _ in range(settings.MAP_HEIGHT)]
        base_density = 0.03 + (self.current_level * 0.01) 
        cluster_chance = 0.45
        
        center_x = settings.MAP_WIDTH // 2
        center_y = settings.MAP_HEIGHT // 2

        # Creating Safe Zones in a single step
        # We use set comprehension to populate the static zones all at once
        safe_paths = {
            (cx, cy)
            for cy in range(center_y - 3, center_y + 3)
            for cx in range(center_x - 5, center_x + 5)
        } | {
            (cx, cy)
            for cy in range(settings.MAP_HEIGHT - 4, settings.MAP_HEIGHT - 1)
            for cx in range(1, 5)
        } | {
            (cx, cy)
            for cy in range(settings.MAP_HEIGHT - 4, settings.MAP_HEIGHT - 1)
            for cx in range(settings.MAP_WIDTH - 5, settings.MAP_WIDTH - 1)
        }

        # Guaranteed random walks
        for start_x in [settings.MAP_WIDTH // 4, settings.MAP_WIDTH // 2, (settings.MAP_WIDTH * 3) // 4]:
            cx, cy = start_x, settings.MAP_HEIGHT - 2
            while cy >= start_row:
                safe_paths.update([(cx, cy), (cx + 1, cy) if cx < settings.MAP_WIDTH - 2 else (cx, cy)])
                roll = random.random()
                if roll < 0.5: cy -= 1
                elif roll < 0.75 and cx > 2: cx -= 1
                elif cx < settings.MAP_WIDTH - 3: cx += 1

        # Light up the outermost columns one block higher.
        grid[start_row - 1][0] = True
        grid[start_row - 1][settings.MAP_WIDTH - 1] = True

        # Merging the Edges and Logic loop
        # We evaluate the edges and clustering in the same pass
        for y in range(start_row, settings.MAP_HEIGHT):
            for x in range(settings.MAP_WIDTH):

                # Immediate edge rule
                if x == 0 or x == settings.MAP_WIDTH - 1 or y == settings.MAP_HEIGHT - 1:
                    grid[y][x] = True
                    continue

                # Protected areas
                if (x, y) in safe_paths or (start_row <= y <= start_row + 2 and settings.MAP_WIDTH // 2 - 2 <= x <= settings.MAP_WIDTH // 2 + 2):
                    continue

                # Clustering
                chance = cluster_chance if (grid[y-1][x] or grid[y][x-1]) else base_density
                if random.random() < chance:
                    grid[y][x] = True

        # Automatic Smoothing (Cellular Automata)
        for _ in range(2): 
            for y in range(start_row + 1, settings.MAP_HEIGHT - 1):
                for x in range(1, settings.MAP_WIDTH - 1):
                    if not grid[y][x] and (x, y) not in safe_paths:
                        neighbors = sum([grid[y-1][x], grid[y+1][x], grid[y][x-1], grid[y][x+1]])
                        if neighbors >= 3:
                            grid[y][x] = True

        # Physical Instantiation
        for y in range(start_row - 1, settings.MAP_HEIGHT):
            for x in range(settings.MAP_WIDTH):
                
                pixel_x = settings.MAP_RENDER_OFFSET_X + x * settings.TILE_SIZE
                pixel_y = settings.MAP_RENDER_OFFSET_Y + y * settings.TILE_SIZE_Y 

                # Prevent decorative elements from being drawn in the empty space of the extra row.
                if y == start_row - 1 and not grid[y][x]:
                    continue
                
                if grid[y][x]:
                    self.objects.append(Prop(pixel_x, pixel_y, self.brick_texture, random.randint(0, 2), solid=True))

                elif random.random() < 0.12 and (x, y) not in safe_paths:
                    self.objects.append(Prop(pixel_x, pixel_y, self.prop_texture, random.randint(0, self.max_prop_frame), solid=False))

    def get_solid_rects(self) -> list[pygame.Rect]:
        """
                Returns a list of pygame.Rect for all objects where solid == True.
                Used for collision detection in PlayState.
        """
        return [obj.get_collision_rect() for obj in self.objects if obj.solid]

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        for obj in self.objects:
            obj.render(surface)
        for entity in self.entities:
            entity.render(surface)