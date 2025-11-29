from typing import Optional, Literal, Callable, Literal
from pydantic import BaseModel, PrivateAttr, Field


class VisualProperties(BaseModel):
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    occupied_by: Literal['Player', 'Opponent', None] = None


class BoardSpace(BaseModel):
    name: str
    space_type: Literal["property", "action"]
    space_id: str
    space_index: int
    visual_properties: VisualProperties = Field(default_factory=VisualProperties)


class PropertySpace(BoardSpace):

    _rent_func: Optional[Callable] = PrivateAttr()

    space_type: Literal["property"] = "property"
    purchase_price: int
    mortgage_value: int

    @property
    def rent_price(self) -> int:
        _rent_func = getattr(self, "_rent_func") or (lambda self: self.purchase_price // 10)
        return _rent_func(self)


class ActionSpace(BoardSpace):
    space_type: Literal["action"] = "action"
    action: Literal["tax", "draw_chest", "draw_chance", "collect_200", "go_to_jail", "no_effect"]


def space_from_json(data: dict) -> BoardSpace:
    if data.get("space_type") == "property":
        return PropertySpace(**data)
    elif data.get("space_type") == "action":
        return ActionSpace(**data)
    else:
        raise ValueError(f"Unknown space_type: {data.get('space_type')}")
