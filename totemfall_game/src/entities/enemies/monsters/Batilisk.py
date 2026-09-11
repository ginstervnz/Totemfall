from src.entities.enemies.BaseEnemy import BaseEnemy
from src.entities.enemies.states.EnemyWalkState import EnemyWalkState
from gale.state import StateMachine
from gale.animation import Animation

class Batilisk(BaseEnemy):
    def __init__(self, x: float, y: float):
        # Firts dates for enemies
        super().__init__(x, y, hp=10, speed=30)
        self.width = 20
        self.height = 18
        
        self.animations = {
            'walk': Animation([0, 1, 2, 3], 0.15)
        }
        
        self.state_machine = StateMachine({
            'walk': lambda sm: EnemyWalkState(self, sm)
        })
        self.state_machine.change('walk')

    def render(self, surface) -> None:
        super().render(surface, 'batilisk', 'batilisk_frames')