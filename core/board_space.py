from typing import Dict, Any, Optional, Literal, Callable
from pydantic import BaseModel, Field, PrivateAttr


class BoardSpace(BaseModel):
    name: str
    space_type: Literal["property", "action"]
    space_id: str
    space_index: int


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
