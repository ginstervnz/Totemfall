from src.world.ProceduralRoom import ProceduralRoom

class WaterRoom(ProceduralRoom):
    def __init__(self, player) -> None:
            super().__init__(player, brick_texture="water", prop_texture="props_swamp", max_prop_frame=5)