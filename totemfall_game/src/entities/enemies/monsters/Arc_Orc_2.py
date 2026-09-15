from src.entities.enemies.BaseEnemy import BaseEnemy
from src.entities.enemies.states.EnemyRangedWalkState import EnemyRangedWalkState
from src.entities.enemies.states.EnemyRangedAttackState import EnemyRangedAttackState
from gale.state import StateMachine
from gale.animation import Animation

class Arc_Orc_2(BaseEnemy):
    def __init__(self, x: float, y: float):
        
        super().__init__(x, y, hp=15, speed=25) 
        self.width = 16 
        self.height = 16

        self.texture_id = 'goblin_2'
        self.attack_range = 120
        self.projectile_config = {'speed': 120, 'texture': 'arrow', 'frames': [0,1,2,3,4,5]}
        self.animations = {
            'walk': Animation([0, 1, 2,3], 0.2),
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
        super().render(surface, 'goblin_2', 'goblin_2_frames')