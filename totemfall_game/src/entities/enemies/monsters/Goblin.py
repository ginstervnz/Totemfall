from src.entities.enemies.BaseEnemy import BaseEnemy
from src.entities.enemies.states.EnemyWalkState import EnemyWalkState
from src.entities.enemies.states.EnemyAttackState import EnemyAttackState
from gale.state import StateMachine
from gale.animation import Animation

class Goblin(BaseEnemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, hp=15, speed=25) 
        self.width = 23 
        self.height = 23

        self.texture_id = 'goblin2'
        
        # --- ENEMY SPECIFIC MELEE CONFIG ---
        self.attack_texture = 'attack_spear'
        self.attack_frames = [0, 1, 2, 3] 
        self.attack_damage_frame = 3 # The frame where the spear is fully extended
        
        self.animations = {
            'walk': Animation([0, 1, 2, 3], 0.2),
        }
        
        self.state_machine = StateMachine({
            'walk': lambda sm: EnemyWalkState(self, sm),
            'attack': lambda sm: EnemyAttackState(self, sm)
        })
        self.state_machine.change('walk')

    def render(self, surface) -> None:
        super().render(surface, 'goblin2', 'goblin2_frames')