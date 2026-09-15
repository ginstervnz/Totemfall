import pygame
import random
import math
import settings

class BaseCard:
    def __init__(self, x: float, y: float, title: str, description: str, icon_id: str, frame_id: str = 'card_base'):
        self.x = x
        self.y = y
        # Return to a balanced pixel-art size
        self.width = 72  
        self.height = 108
        
        self.title = title
        self.description = description
        self.icon_id = icon_id
        self.frame_id = frame_id
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_hovered = False
        
        self.scale = 1.0
        self.locked = False 
        
        self.particles = []
        self.particle_timer = 0.0

    def update(self, mx: float, my: float, dt: float) -> None:
        self.rect.x = self.x
        self.rect.y = self.y

        # Dynamic hover scaling
        if not self.locked:
            self.is_hovered = self.rect.collidepoint(mx, my)
            target_scale = 1.15 if self.is_hovered else 1.0
            self.scale += (target_scale - self.scale) * 15 * dt
        else:
            self.is_hovered = False

        # Particle logic with global coordinates
        for p in self.particles:
            p['y'] += p['speed'] * dt
            p['anim_timer'] += dt
            if p['anim_timer'] > 0.08:
                p['anim_timer'] = 0
                p['frame'] = (p['frame'] + 1) % 4
            p['life'] -= dt
            
        self.particles = [p for p in self.particles if p['life'] > 0]

        if self.is_hovered and not self.locked:
            self.particle_timer += dt
            if self.particle_timer > 0.1:
                self.particle_timer = 0
                p_type = random.choice(['sparkle', 'sparkle_2'])
                
                scaled_w = self.width * self.scale
                scaled_h = self.height * self.scale
                offset_x = self.x - (scaled_w - self.width) / 2
                offset_y = self.y - (scaled_h - self.height) / 2
                
                self.particles.append({
                    'x': offset_x + random.randint(10, int(scaled_w) - 10),
                    'y': offset_y + scaled_h - 10,
                    'speed': random.uniform(15, 30),
                    'anim_timer': 0.0,
                    'frame': 0,
                    'life': random.uniform(0.5, 1.2),
                    'type': p_type
                })

    def _render_text_with_autoscale(self, text: str, font: pygame.font.Font, max_width: int, color: tuple) -> pygame.Surface:
        """Renders text and scales it down if it exceeds the card's maximum width."""
        surf = font.render(text, True, color)
        if surf.get_width() > max_width:
            scale_factor = max_width / surf.get_width()
            new_width = int(surf.get_width() * scale_factor)
            new_height = int(surf.get_height() * scale_factor)
            # Use standard scale for pixel art to avoid blur
            surf = pygame.transform.scale(surf, (new_width, new_height))
        return surf

    def render(self, surface: pygame.Surface) -> None:
        # 1. LOCAL SURFACE 
        card_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.frame_id in settings.TEXTURES:
            raw_img = settings.TEXTURES[self.frame_id]
            card_img = pygame.transform.scale(raw_img, (self.width, self.height))
            card_surf.blit(card_img, (0, 0)) 
        
        # Hover glow
        if self.is_hovered and not self.locked:
            glow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            time_ms = pygame.time.get_ticks()
            pulse = (math.sin(time_ms * 0.005) + 1) / 2  
            alpha = int(50 + (100 * pulse)) 
            soft_gold = (255, 215, 0, alpha) 
            pygame.draw.rect(glow_surf, soft_gold, glow_surf.get_rect(), width=3, border_radius=6)
            card_surf.blit(glow_surf, (0, 0))
            
        # Icon
        if self.icon_id in settings.TEXTURES:
            icon = settings.TEXTURES[self.icon_id]
            icon_x = (self.width / 2) - (icon.get_width() / 2)
            card_surf.blit(icon, (icon_x, 15)) 
            
        # Text with Auto-Scale Feature
        if 'small' in settings.FONTS:
            font = settings.FONTS['small']
            
            # Render title dynamically
            title_surf = self._render_text_with_autoscale(self.title, font, self.width - 8, (255, 255, 255))
            title_x = (self.width / 2) - (title_surf.get_width() / 2)
            card_surf.blit(title_surf, (title_x, 50)) 
            
            # Render description dynamically
            desc_surf = self._render_text_with_autoscale(self.description, font, self.width - 12, (200, 200, 200))
            desc_x = (self.width / 2) - (desc_surf.get_width() / 2)
            card_surf.blit(desc_surf, (desc_x, 75)) 

        # 2. MAIN SURFACE: Zoom Application
        scaled_w = int(self.width * self.scale)
        scaled_h = int(self.height * self.scale)
        scaled_card = pygame.transform.scale(card_surf, (scaled_w, scaled_h))
        
        offset_x = self.x - (scaled_w - self.width) / 2
        offset_y = self.y - (scaled_h - self.height) / 2
        
        surface.blit(scaled_card, (offset_x, offset_y))

        # 3. MAIN SURFACE: Particles 
        for p in self.particles:
            p_type = p['type']
            frames_key = f'{p_type}_frames'
            if p_type in settings.TEXTURES and frames_key in settings.FRAMES:
                frame_rect = settings.FRAMES[frames_key][p['frame']]
                img = settings.TEXTURES[p_type].subsurface(frame_rect)
                scaled_img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                surface.blit(scaled_img, (p['x'], p['y']))

    def apply_effect(self, player, play_state) -> None:
        pass