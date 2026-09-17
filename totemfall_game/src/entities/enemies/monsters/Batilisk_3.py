from src.entities.enemies.BaseEnemy import BaseEnemy
from src.entities.enemies.states.EnemyRangedWalkState import EnemyRangedWalkState
from src.entities.enemies.states.EnemyRangedAttackState import EnemyRangedAttackState
from gale.state import StateMachine
from gale.animation import Animation

class Batilisk_3(BaseEnemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, hp=20, speed=25) 
        self.width = 29 
        self.height = 22
        self.attack_range = 120

        self.texture_id = 'batilisk_3'
        
        self.projectile_config = {
            'speed': 90,
            'texture': 'fire_bolt', # Must be registered in settings.py
            'frames': [0, 1, 2, 3] 
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
        super().render(surface, 'batilisk_3', 'batilisk_3_frames')