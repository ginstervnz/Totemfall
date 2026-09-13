from src.world.ProceduralRoom import ProceduralRoom
from src.entities.enemies.monsters.Slime import Slime
from src.entities.enemies.monsters.Slime_2 import Slime_2
from src.entities.enemies.monsters.Slime_3 import Slime_3
from src.entities.enemies.monsters.Arc_Orc import Arc_Orc
from src.entities.enemies.monsters.Arc_Orc_2 import Arc_Orc_2
from src.entities.enemies.monsters.Arc_Orc_3 import Arc_Orc_3
from src.entities.enemies.monsters.Lizard import Lizard
from src.entities.enemies.monsters.Lizard_2 import Lizard_2
from src.entities.enemies.monsters.Lizard_3 import Lizard_3
from src.entities.enemies.monsters.Skeleton_3 import Skeleton_3
from src.entities.enemies.monsters.Goblin import Goblin
from src.entities.enemies.monsters.Goblin_2 import Goblin_2


class WaterRoom(ProceduralRoom):
    def __init__(self, player) -> None:
            super().__init__(player, brick_texture="water", prop_texture="props_swamp", max_prop_frame=5)

            self.allowed_enemies = [Arc_Orc,Arc_Orc_2,Arc_Orc_3,Goblin,Goblin_2,Slime,Slime_2,Slime_3,Lizard,Lizard_2,Lizard_3,Skeleton_3]