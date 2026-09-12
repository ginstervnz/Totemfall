from src.world.ProceduralRoom import ProceduralRoom

class SwampRoom(ProceduralRoom):
    def __init__(self, player) -> None:
        super().__init__(player, brick_texture="brick", prop_texture="props_swamp", max_prop_frame=5)