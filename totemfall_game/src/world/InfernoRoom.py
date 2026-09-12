from src.world.ProceduralRoom import ProceduralRoom

class InfernoRoom(ProceduralRoom):
    def __init__(self, player) -> None:
        super().__init__(player, brick_texture="brimstone", prop_texture="props_inferno", max_prop_frame=2)