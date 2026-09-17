from src.world.ProceduralRoom import ProceduralRoom
from src.entities.enemies.monsters.Arc_Orc import Arc_Orc
from src.entities.enemies.monsters.Arc_Orc_2 import Arc_Orc_2
from src.entities.enemies.monsters.Arc_Orc_3 import Arc_Orc_3
from src.entities.enemies.monsters.Goblin import Goblin
from src.entities.enemies.monsters.Goblin_2 import Goblin_2
from src.entities.enemies.monsters.Goblin_3 import Goblin_3
from src.entities.enemies.monsters.Batilisk_2 import Batilisk_2
from src.entities.enemies.monsters.Batilisk import Batilisk
from src.entities.enemies.monsters.Dragon import Dragon



class RockRoom(ProceduralRoom):
    def __init__(self, player) -> None:
            super().__init__(player, brick_texture="rock", prop_texture="props_corpses", max_prop_frame=5)

            self.allowed_enemies = [Arc_Orc,Arc_Orc_2,Arc_Orc_3,Goblin,Goblin_2,Goblin_3, Batilisk,Batilisk_2,Dragon] 