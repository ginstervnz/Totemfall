from gale.state import BaseState

class BaseEntityState(BaseState):
    def __init__(self, entity, state_machine):
        super().__init__(state_machine)
        self.entity = entity