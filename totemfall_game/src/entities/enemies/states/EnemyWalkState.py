from src.entities.BaseEntityState import BaseEntityState

class EnemyWalkState(BaseEntityState):
    def enter(self) -> None:
        self.entity.current_animation = self.entity.animations['walk']

    def update(self, dt: float) -> None:
        self.entity.y += self.entity.speed * dt
        