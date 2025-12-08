from typing import Optional, Literal, List, Literal, Set
from pydantic import BaseModel, PrivateAttr, Field


class VisualProperties(BaseModel):
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    occupied_by: Optional[List[str]] = Field(default_factory=list)


class BoardSpace(BaseModel):
    name: str
    space_type: Literal["property", "action"]
    space_id: str
    space_index: int
    visual_properties: VisualProperties = Field(default_factory=VisualProperties)

    def add_occupant(self, user_id: str) -> None:
        if user_id not in self.visual_properties.occupied_by:
            self.visual_properties.occupied_by.append(user_id)
    
    def remove_occupant(self, user_id: str) -> None:
        while user_id in self.visual_properties.occupied_by:
            self.visual_properties.occupied_by.remove(user_id)


class PropertySpace(BoardSpace):
    space_type: Literal["property"] = "property"
    purchase_price: int
    mortgage_value: int
    hotels: int = 0
    rent_prices: List[int] = []
    owned_by: Optional[str] = None # user_id of the owner, None if unowned
    """User ID or None"""


class ActionSpace(BoardSpace):
    space_type: Literal["action"] = "action"
    action: Literal["tax", "draw_chest", "draw_chance", "go_to_jail", "no_effect"]


def space_from_json(data: dict) -> BoardSpace:
    if data.get("space_type") == "property":
        return PropertySpace(**data)
    elif data.get("space_type") == "action":
        return ActionSpace(**data)
    else:
        raise ValueError(f"Unknown space_type: {data.get('space_type')}")
