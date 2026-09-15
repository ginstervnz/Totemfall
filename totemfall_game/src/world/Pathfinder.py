import heapq
import settings

class Pathfinder:
    def __init__(self, room):
        self.room = room

    def get_path(self, start_x: float, start_y: float, target_x: float, target_y: float) -> list:
        """Returns a list of coordinates (pixels) to reach the target."""
        if not hasattr(self.room, 'grid'):
            return []

        # Convert Pixels to Matrix Indices
        start_col = int((start_x - settings.MAP_RENDER_OFFSET_X) // settings.TILE_SIZE)
        start_row = int((start_y - settings.MAP_RENDER_OFFSET_Y) // settings.TILE_SIZE_Y)
        
        target_col = int((target_x - settings.MAP_RENDER_OFFSET_X) // settings.TILE_SIZE)
        target_row = int((target_y - settings.MAP_RENDER_OFFSET_Y) // settings.TILE_SIZE_Y)

        # Safety clamping to ensure we don't go off-list.
        start_col = max(0, min(settings.MAP_WIDTH - 1, start_col))
        start_row = max(0, min(settings.MAP_HEIGHT - 1, start_row))
        target_col = max(0, min(settings.MAP_WIDTH - 1, target_col))
        target_row = max(0, min(settings.MAP_HEIGHT - 1, target_row))

        start_node = (start_col, start_row)
        target_node = (target_col, target_row)

        # Classic A* (A-Star) Algorithm
        open_list = []
        heapq.heappush(open_list, (0, start_node))
        came_from = {}
        g_score = {start_node: 0}

        # Set for tracking nodes that have already been fully evaluated
        closed_set = set()

        # Allowed movements (Up, Down, Left, Right)
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),   # Orthogonal
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # Diagonals
        ]

        while open_list:
            current = heapq.heappop(open_list)[1]

            # If we have already evaluated this node optimally, we ignore it.
            if current in closed_set:
                continue
            
            closed_set.add(current) # We mark it as processed.

            if current == target_node:
                return self._reconstruct_path(came_from, current)

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)

                # Validate matrix bounds
                if 0 <= neighbor[0] < settings.MAP_WIDTH and 0 <= neighbor[1] < settings.MAP_HEIGHT:
                    # Verify if it is a solid wall.
                    if self.room.grid[neighbor[1]][neighbor[0]]:
                        continue 

                    # If the movement is diagonal (both dx and dy are non-zero)
                    if dx != 0 and dy != 0:
                        # We checked the two adjacent walls to ensure there is space to pass.
                        if self.room.grid[current[1]][current[0] + dx] or self.room.grid[current[1] + dy][current[0]]:
                            continue # If there is a wall on the sides, diagonal movement is blocked.

                    step_cost = 1.414 if (dx != 0 and dy != 0) else 1.0
                    tentative_g_score = g_score[current] + step_cost

                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        # Euclidean Heuristic
                        h_score = ((neighbor[0] - target_node[0])**2 + (neighbor[1] - target_node[1])**2)**0.5
                        f_score = tentative_g_score + h_score
                        heapq.heappush(open_list, (f_score, neighbor))

        return [] # Returns empty if there is no possible path (trapped).

    def _reconstruct_path(self, came_from: dict, current: tuple) -> list:
        """Convert the grid nodes back into centered pixels for the enemy to walk on."""
        path = []
        while current in came_from:
            # Convert (Column, Row) to (Pixel X, Pixel Y) centered on the block
            pixel_x = settings.MAP_RENDER_OFFSET_X + (current[0] * settings.TILE_SIZE) + (settings.TILE_SIZE // 2)
            pixel_y = settings.MAP_RENDER_OFFSET_Y + (current[1] * settings.TILE_SIZE_Y) + (settings.TILE_SIZE_Y // 2)
            path.append((pixel_x, pixel_y))
            current = came_from[current]
            
        path.reverse()
        return path