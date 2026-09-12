from src.world.ProceduralRoom import ProceduralRoom

class CatacombsRoom(ProceduralRoom):
    def __init__(self, player) -> None:
        super().__init__(player, brick_texture="lava", prop_texture="props_catacombs", max_prop_frame=5)