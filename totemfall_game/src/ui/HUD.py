import pygame
import settings

class HUD:

    # Class variables
    _full_heart = None
    _empty_heart = None
    
    _cached_level_val = None
    _cached_level_surface = None
    
    _cached_player_lvl_val = None
    _cached_player_lvl_surface = None

    @classmethod
    def _initialize_assets(cls):
        """Pre-process and scale heavy assets once."""
        heart_img = settings.TEXTURES['heart']
        cls._full_heart = pygame.transform.scale(heart_img.subsurface(settings.FRAMES['heart_frames'][0]), (12, 8))
        cls._empty_heart = pygame.transform.scale(heart_img.subsurface(settings.FRAMES['heart_frames'][2]), (12, 8))

    @classmethod
    def render(cls, surface, player, totem, current_level, random_mode, cursor_frame):
        # Lazy Initialization (Deferred loading)
        if cls._full_heart is None:
            cls._initialize_assets()

        # RENDER TOTEM HEARTS (Direct from cache)
        for i in range(totem.max_hp):
            surface.blit(cls._full_heart if i < totem.hp else cls._empty_heart, (10 + (i * 16), 10))

        # WORLD-LEVEL TEXT (Smart Caching)
        level_str = "Level: INF" if random_mode else f"Level: {current_level}"
        # It is only rasterized again if the text has changed.
        if cls._cached_level_val != level_str:
            cls._cached_level_val = level_str
            cls._cached_level_surface = settings.FONTS['small'].render(level_str, True, (255, 255, 255))
        surface.blit(cls._cached_level_surface, (10, 26))

        # PLAYER MANA BAR
        bar_width = 30
        bar_x = player.x + (player.width / 2) - (bar_width / 2)
        bar_y = player.y + player.height + 4
        current_bar_width = max(0, int(bar_width * (player.mana / player.max_mana)))
        pygame.draw.rect(surface, (20, 20, 30), (bar_x, bar_y, bar_width, 4))
        if current_bar_width > 0:
            pygame.draw.rect(surface, (80, 150, 220), (bar_x, bar_y, current_bar_width, 4))

        # EXPERIENCE BAR
        xp_frame = settings.TEXTURES['xp_frame']
        xp_fill = settings.TEXTURES['xp_fill']
        bar_x = settings.VIRTUAL_WIDTH - xp_frame.get_width() - 10
        surface.blit(xp_frame, (bar_x, 10))
        
        if player.xp > 0:
            current_fill_width = max(1, int(xp_fill.get_width() * (player.xp / player.xp_to_next_level)))
            surface.blit(xp_fill.subsurface(pygame.Rect(0, 0, current_fill_width, xp_fill.get_height())), (bar_x + 2, 19))

        # PLAYER LEVEL (Smart Caching)
        player_lvl = getattr(player, 'level', 1)
        if cls._cached_player_lvl_val != player_lvl:
            cls._cached_player_lvl_val = player_lvl
            cls._cached_player_lvl_surface = settings.FONTS['small'].render(f"LVL: {player_lvl}", True, (255, 215, 0))
        surface.blit(cls._cached_player_lvl_surface, (400, 30))

        # RENDER CURSOR
        mx, my = pygame.mouse.get_pos()
        frame_rect = settings.FRAMES['cursor_frames'][cursor_frame]
        surface.blit(settings.TEXTURES['cursor'].subsurface(frame_rect), 
                    ((mx * (settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH)) - (frame_rect.width / 2), 
                     (my * (settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT)) - (frame_rect.height / 2)))