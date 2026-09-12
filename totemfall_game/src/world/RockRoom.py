from src.world.ProceduralRoom import ProceduralRoom

class RockRoom(ProceduralRoom):
    def __init__(self, player) -> None:
            super().__init__(player, brick_texture="rock", prop_texture="props_corpses", max_prop_frame=5) 