from typing import Any, Dict


class UserState:

    user_id: Dict[str, Any]
    money_dollars: int

    def __init__(self, user_id: str, money_dollars: int = 0):
        self.user_id = user_id
        self.money_dollars = money_dollars

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "money_dollars": self.money_dollars
        }
    
    def add_money(self, amount: int) -> None:
        self.money_dollars += amount

    def subtract_money(self, amount: int) -> None:
        self.money_dollars -= amount
