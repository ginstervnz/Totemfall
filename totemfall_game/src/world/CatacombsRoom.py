from src.world.ProceduralRoom import ProceduralRoom
from src.entities.enemies.monsters.Skeleton import Skeleton
from src.entities.enemies.monsters.Skeleton_2 import Skeleton_2
from src.entities.enemies.monsters.Skeleton_3 import Skeleton_3
from src.entities.enemies.monsters.Slime import Slime
from src.entities.enemies.monsters.Slime_2 import Slime_2
from src.entities.enemies.monsters.Slime_3 import Slime_3
from src.entities.enemies.monsters.Ghost import Ghost
from src.entities.enemies.monsters.Ghost_2 import Ghost_2
from src.entities.enemies.monsters.Lizard import Lizard
from src.entities.enemies.monsters.Lizard_2 import Lizard_2


class CatacombsRoom(ProceduralRoom):
    def __init__(self, player) -> None:
        super().__init__(player, brick_texture="lava", prop_texture="props_catacombs", max_prop_frame=5)

        self.allowed_enemies = [Skeleton,Skeleton_2,Skeleton_3,Slime,Slime_2,Slime_3,Ghost_2,Ghost,Lizard,Lizard_2] 