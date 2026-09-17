from src.entities.enemies.BaseEnemy import BaseEnemy
from src.entities.enemies.states.EnemyWalkState import EnemyWalkState
from src.entities.enemies.states.EnemyAttackState import EnemyAttackState
from gale.state import StateMachine
from gale.animation import Animation

class Batilisk(BaseEnemy):
    def __init__(self, x: float, y: float):
        # Firts dates for enemies
        super().__init__(x, y, hp=15, speed=25)
        self.width = 20
        self.height = 18

        self.texture_id = 'batilisk'

        # --- ENEMY SPECIFIC MELEE CONFIG ---
        self.attack_texture = 'attack_swing'
        self.attack_frames = [0, 1, 2, 3] 
        self.attack_damage_frame = 3

        
        self.animations = {
            'walk': Animation([0, 1, 2, 3], 0.15)
        }
        
        self.state_machine = StateMachine({
            'walk': lambda sm: EnemyWalkState(self, sm),
            'attack': lambda sm: EnemyAttackState(self, sm),
        })
        self.state_machine.change('walk')

    def render(self, surface) -> None:
        super().render(surface, 'batilisk', 'batilisk_frames')