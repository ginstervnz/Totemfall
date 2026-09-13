from src.world.ProceduralRoom import ProceduralRoom
from src.entities.enemies.monsters.Minotaur import Minotaur
from src.entities.enemies.monsters.Minotaur_2 import Minotaur_2
from src.entities.enemies.monsters.Minotaur_3 import Minotaur_3
from src.entities.enemies.monsters.Batilisk_3 import Batilisk_3
from src.entities.enemies.monsters.Ghost_3 import Ghost_3
from src.entities.enemies.monsters.Lizard_3 import Lizard_3

class InfernoRoom(ProceduralRoom):
    def __init__(self, player) -> None:
        super().__init__(player, brick_texture="brimstone", prop_texture="props_inferno", max_prop_frame=2)

        self.allowed_enemies = [Minotaur,Minotaur_2,Minotaur_3,Ghost_3,Lizard_3, Batilisk_3] 