from src.entities.enemies.BaseEnemy import BaseEnemy
from src.entities.enemies.states.EnemyRangedWalkState import EnemyRangedWalkState
from src.entities.enemies.states.EnemyRangedAttackState import EnemyRangedAttackState
from gale.state import StateMachine
from gale.animation import Animation

class Ghost_2(BaseEnemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, hp=20, speed=20) 
        self.width = 29 
        self.height = 22
        self.attack_range = 100

        self.texture_id = 'ghost_2'
        
        self.projectile_config = {
            'speed': 90,
            'texture': 'ghost_bolt', # Must be registered in settings.py
            'frames': [0, 1, 2, 3,4,5,6,7] 
        }
        
        self.animations = {
            'walk': Animation([0, 1, 2, 3], 0.15),
        }
        
        self.state_machine = StateMachine({
            'walk': lambda sm: EnemyRangedWalkState(self, sm), 
            'attack': lambda sm: EnemyRangedAttackState(self, sm)
        })
        self.state_machine.change('walk')
        
        self.just_fired = False
        self.shoot_angle = 0.0
        self.shoot_x = 0.0 
        self.shoot_y = 0.0

    def render(self, surface) -> None:
        super().render(surface, 'ghost_2', 'ghost_2_frames')