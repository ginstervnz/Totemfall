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
        self.allowed_enemies = []

        # Variable to store the rectangles in memory
        self._cached_rects = None

        self._generate_procedural_layout()

    def _generate_procedural_layout(self) -> None:
        self._cached_rects = None
        self.objects.clear()
        start_row = 4
        self.grid = [[False for _ in range(settings.MAP_WIDTH)] for _ in range(settings.MAP_HEIGHT)]
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
        self.grid[start_row - 1][0] = True
        self.grid[start_row - 1][settings.MAP_WIDTH - 1] = True

        # Merging the Edges and Logic loop
        # We evaluate the edges and clustering in the same pass
        for y in range(start_row, settings.MAP_HEIGHT):
            for x in range(settings.MAP_WIDTH):

                # Immediate edge rule
                if x == 0 or x == settings.MAP_WIDTH - 1 or y == settings.MAP_HEIGHT - 1:
                    self.grid[y][x] = True
                    continue

                # Protected areas
                if (x, y) in safe_paths or (start_row <= y <= start_row + 2 and settings.MAP_WIDTH // 2 - 2 <= x <= settings.MAP_WIDTH // 2 + 2):
                    continue

                # Clustering
                chance = cluster_chance if (self.grid[y-1][x] or self.grid[y][x-1]) else base_density
                if random.random() < chance:
                    self.grid[y][x] = True

        # Automatic Smoothing (Cellular Automata)
        for _ in range(2): 
            for y in range(start_row + 1, settings.MAP_HEIGHT - 1):
                for x in range(1, settings.MAP_WIDTH - 1):
                    if not self.grid[y][x] and (x, y) not in safe_paths:
                        neighbors = sum([self.grid[y-1][x], self.grid[y+1][x], self.grid[y][x-1], self.grid[y][x+1]])
                        if neighbors >= 3:
                            self.grid[y][x] = True


        # Map Validation using BFS (Flood Fill)
        # Start the scan from a guaranteed safe zone (the bottom center of the map).
        start_x = settings.MAP_WIDTH // 2
        start_y = settings.MAP_HEIGHT - 2
        
        reachable_nodes = set()
        queue = [(start_x, start_y)]
        reachable_nodes.add((start_x, start_y))
        
        # Orthogonal directions (up, down, left, right)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        # Spread the water (Flood Fill) through all connected corridors.
        while queue:
            cx, cy = queue.pop(0)
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                # If it is within the map, is a corridor (False), and has not been visited
                if 0 <= nx < settings.MAP_WIDTH and 0 <= ny < settings.MAP_HEIGHT:
                    if not self.grid[ny][nx] and (nx, ny) not in reachable_nodes:
                        reachable_nodes.add((nx, ny))
                        queue.append((nx, ny))
                        
        # Culling:
        # We traverse the map. If there is a corridor (False) that the BFS did not reach, it is a closed-off island.
        for y in range(start_row, settings.MAP_HEIGHT - 1):
            for x in range(1, settings.MAP_WIDTH - 1):
                if not self.grid[y][x] and (x, y) not in reachable_nodes:
                    # We turned the island into a solid wall.
                    self.grid[y][x] = True

        # Physical Instantiation
        for y in range(start_row - 1, settings.MAP_HEIGHT):
            for x in range(settings.MAP_WIDTH):
                
                pixel_x = settings.MAP_RENDER_OFFSET_X + x * settings.TILE_SIZE
                pixel_y = settings.MAP_RENDER_OFFSET_Y + y * settings.TILE_SIZE_Y 


                vis_x = pixel_x - 2
                vis_y = pixel_y - 3

                # Prevent decorative elements from being drawn in the empty space of the extra row.
                if y == start_row - 1 and not self.grid[y][x]:
                    continue
                
                if self.grid[y][x]:
                    self.objects.append(Prop(vis_x, vis_y, self.brick_texture, random.randint(0, 2), solid=True))

                elif random.random() < 0.12 and (x, y) not in safe_paths:
                    self.objects.append(Prop(pixel_x, pixel_y, self.prop_texture, random.randint(0, self.max_prop_frame), solid=False))

    def get_solid_rects(self) -> list[pygame.Rect]:
        """
                Returns a list of pygame.Rect for all objects where solid == True.
                Used for collision detection in PlayState.
        """

        # If we have already calculated the walls and no one has broken them, we return the report.
        if self._cached_rects is not None:
            return self._cached_rects
        
        rects = []
        visited = [[False for _ in range(settings.MAP_WIDTH)] for _ in range(settings.MAP_HEIGHT)]

        for y in range(settings.MAP_HEIGHT):
            for x in range(settings.MAP_WIDTH):
                
                # If we find a wall that has NOT yet been merged
                if self.grid[y][x] and not visited[y][x]:
                    
                    # Expand as far as possible to the right.
                    current_width = 0
                    while (x + current_width < settings.MAP_WIDTH and 
                           self.grid[y][x + current_width] and 
                           not visited[y][x + current_width]):
                        current_width += 1
                        
                    # Expand downwards while maintaining that exact width.
                    current_height = 0
                    can_expand_down = True
                    
                    while y + current_height < settings.MAP_HEIGHT and can_expand_down:
                        # We check whether the entire bottom row matches our block.
                        for check_x in range(current_width):
                            if (not self.grid[y + current_height][x + check_x] or 
                                visited[y + current_height][x + check_x]):
                                can_expand_down = False
                                break
                        if can_expand_down:
                            current_height += 1
                            
                    # Mark this entire large 2D rectangle as "visited".
                    for mark_y in range(current_height):
                        for mark_x in range(current_width):
                            visited[y + mark_y][x + mark_x] = True
                            
                    # Calculate the actual pixels and create the giant hitbox.
                    pixel_x = settings.MAP_RENDER_OFFSET_X + x * settings.TILE_SIZE
                    pixel_y = settings.MAP_RENDER_OFFSET_Y + y * settings.TILE_SIZE_Y
                    rect_w = current_width * settings.TILE_SIZE
                    rect_h = current_height * settings.TILE_SIZE_Y
                    rects.append(pygame.Rect(pixel_x, pixel_y, rect_w, rect_h))
        self._cached_rects = rects
        return self._cached_rects

    def break_block_at(self, col: int, row: int) -> None:
        """Destroy a physical block and release the logical matrix for A*."""
        # We free the cell in the logic matrix.
        if 0 <= col < settings.MAP_WIDTH and 0 <= row < settings.MAP_HEIGHT:
            self.grid[row][col] = False

            # When breaking a wall, we clear the cache to force a recalculation in the next frame.
            self._cached_rects = None
            
        # We calculate the exact pixel coordinates of that block.
        pixel_x = settings.MAP_RENDER_OFFSET_X + col * settings.TILE_SIZE
        pixel_y = settings.MAP_RENDER_OFFSET_Y + row * settings.TILE_SIZE_Y

        vis_x = pixel_x - 2
        vis_y = pixel_y - 3
        
        # We locate the visual object and remove it from memory.
        for i in range(len(self.objects) - 1, -1, -1):
            obj = self.objects[i]
            if obj.solid and obj.x == vis_x and obj.y == vis_y:
                self.objects.pop(i)
                break

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        for obj in self.objects:
            obj.render(surface)
        for entity in self.entities:
            entity.render(surface)