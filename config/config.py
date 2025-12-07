import json
from pathlib import Path

from models.board_models import space_from_json


with open('data/board_data.jsonl', 'r') as f:
    BOARD_DATA = [json.loads(line) for line in f.readlines()]

template_game_board = [space_from_json(space_json) for space_json in BOARD_DATA]
PROJECT_PATH = Path(__file__).parent.parent
SESSION_PERSIST_PATH = PROJECT_PATH / "data" / "sessions.db"
