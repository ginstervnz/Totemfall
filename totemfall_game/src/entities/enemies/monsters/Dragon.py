from src.entities.enemies.BaseEnemy import BaseEnemy
from src.entities.enemies.states.DragonWalkState import DragonWalkState
from src.entities.enemies.states.EnemyAttackState import EnemyAttackState
from src.entities.enemies.states.EnemyRangedAttackState import EnemyRangedAttackState
from gale.state import StateMachine
from gale.animation import Animation

class Dragon(BaseEnemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, hp=30, speed=15) 
        self.width = 35 
        self.height = 36

        self.texture_id = 'dragon'
        
        # --- MELEE CONFIG (Same logic as Minotaur) ---
        self.melee_range = 35
        self.attack_texture = 'attack_swing'
        self.attack_frames = [0, 1, 2, 3]
        self.attack_damage_frame = 3
        
        # --- RANGED CONFIG (Same logic as Arc_Orc) ---
        self.attack_range = 100 
        self.projectile_config = {'speed': 180, 'texture': 'fire_bolt', 'frames': [0, 1, 2, 3]}
        self.just_fired = False
        self.shoot_angle = 0.0
        self.shoot_x = 0.0 
        self.shoot_y = 0.0
        
        # 3 second delay between fireballs
        self.ranged_cooldown_max = 3.0 
        self.ranged_cooldown_timer = 0.0

        self.animations = {
            'walk': Animation([0, 1, 2, 3], 0.2),
        }
        
        # Register both standard states
        self.state_machine = StateMachine({
            'walk': lambda sm: DragonWalkState(self, sm),
            'attack_melee': lambda sm: EnemyAttackState(self, sm),
            'attack_ranged': lambda sm: EnemyRangedAttackState(self, sm)
        })
        self.state_machine.change('walk')
        
    def update(self, dt: float) -> None:
        # Tick down the fireball cooldown timer
        if self.ranged_cooldown_timer > 0:
            self.ranged_cooldown_timer -= dt
            
        super().update(dt)

    def render(self, surface) -> None:
        super().render(surface, 'dragon', 'dragon_frames')
       