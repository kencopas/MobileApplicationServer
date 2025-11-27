from .board_space import BoardSpace, PropertySpace, ActionSpace
from .user_state import UserState
import random
from models.wsp_schemas import WSPEvent


class GameBoard:
    def __init__(self, spaces: list[BoardSpace]):
        self.spaces = list(sorted(spaces, key=lambda space: space.space_index))
    
    def move_player(self, player_state: UserState) -> None:
        """Move a player based on a dice roll and update the current space."""
        roll = random.randint(2, 12)
        player_state.move_position(roll)

        new_space = self.spaces[player_state.position]
        player_state.update_current_space(new_space)

    def handle_landing(self, player_state: UserState) -> WSPEvent:
        current_space = player_state.current_space
        if isinstance(current_space, PropertySpace):
            return WSPEvent(
                event="landedOnProperty",
                data={
                    "property": current_space.model_dump(),
                    "message": f"You landed on {current_space.name}."
                }
            )
        elif isinstance(current_space, ActionSpace):
            action = current_space.action

            return WSPEvent(
                event="landedOnActionSpace",
                data={
                    "action": current_space.action,
                    "message": f"You landed on {current_space.name} and must perform action: {current_space.action}."
                }
            )
        else:
            return WSPEvent(
                event="landedOnSpace",
                data={
                    "message": f"You landed on {current_space.name}."
                }
            )
