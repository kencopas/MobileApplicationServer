from core.game_board import GameBoard
from core.board_space import PropertySpace, ActionSpace
from core.state_manager import StateManager
from utils.logger import get_logger
from utils.session_manager import SessionManager
from utils.wsp_utils import EventHandlerRegistry
from config.config import SESSION_PERSIST_PATH


state_manager = StateManager()

session_manager = SessionManager(
    persist_path=str(SESSION_PERSIST_PATH),
    log=get_logger("session_manager")
)

event_handler_registry = EventHandlerRegistry(
    log=get_logger("event_handler_registry")
)

board = GameBoard(
    spaces=[
        ActionSpace(
            space_id="go",
            space_index=0,
            name="Go",
            action="collect_200"
        ),
        PropertySpace(
            space_id="mediterranean_avenue",
            space_index=1,
            name="Mediterranean Avenue",
            purchase_price=60,
            mortgage_value=30
        ),
        ActionSpace(
            space_id="community_chest_2",
            space_index=2,
            name="Community Chest",
            action="draw_chest"
        ),
        PropertySpace(
            space_id="baltic_avenue",
            space_index=3,
            name="Baltic Avenue",
            purchase_price=60,
            mortgage_value=30
        ),
        ActionSpace(
            space_id="income_tax",
            space_index=4,
            name="Income Tax",
            action="tax"
        ),
        PropertySpace(
            space_id="reading_railroad",
            space_index=5,
            name="Reading Railroad",
            purchase_price=200,
            mortgage_value=100
        ),
        PropertySpace(
            space_id="oriental_avenue",
            space_index=6,
            name="Oriental Avenue",
            purchase_price=100,
            mortgage_value=50
        ),
        ActionSpace(
            space_id="chance_7",
            space_index=7,
            name="Chance",
            action="draw_chance"
        ),
        PropertySpace(
            space_id="vermont_avenue",
            space_index=8,
            name="Vermont Avenue",
            purchase_price=100,
            mortgage_value=50
        ),
        PropertySpace(
            space_id="connecticut_avenue",
            space_index=9,
            name="Connecticut Avenue",
            purchase_price=120,
            mortgage_value=60
        ),
        ActionSpace(
            space_id="jail_just_visiting",
            space_index=10,
            name="Jail / Just Visiting",
            action="no_effect"
        ),
        PropertySpace(
            space_id="st_charles_place",
            space_index=11,
            name="St. Charles Place",
            purchase_price=140,
            mortgage_value=70
        ),
        PropertySpace(
            space_id="electric_company",
            space_index=12,
            name="Electric Company",
            purchase_price=150,
            mortgage_value=75
        ),
        PropertySpace(
            space_id="states_avenue",
            space_index=13,
            name="States Avenue",
            purchase_price=140,
            mortgage_value=70
        ),
        PropertySpace(
            space_id="virginia_avenue",
            space_index=14,
            name="Virginia Avenue",
            purchase_price=160,
            mortgage_value=80
        ),
        PropertySpace(
            space_id="pennsylvania_railroad",
            space_index=15,
            name="Pennsylvania Railroad",
            purchase_price=200,
            mortgage_value=100
        ),
        PropertySpace(
            space_id="st_james_place",
            space_index=16,
            name="St. James Place",
            purchase_price=180,
            mortgage_value=90
        ),
        ActionSpace(
            space_id="community_chest_17",
            space_index=17,
            name="Community Chest",
            action="draw_chest"
        ),
        PropertySpace(
            space_id="tennessee_avenue",
            space_index=18,
            name="Tennessee Avenue",
            purchase_price=180,
            mortgage_value=90
        ),
        PropertySpace(
            space_id="new_york_avenue",
            space_index=19,
            name="New York Avenue",
            purchase_price=200,
            mortgage_value=100
        ),
        ActionSpace(
            space_id="free_parking",
            space_index=20,
            name="Free Parking",
            action="no_effect"
        ),
        PropertySpace(
            space_id="kentucky_avenue",
            space_index=21,
            name="Kentucky Avenue",
            purchase_price=220,
            mortgage_value=110
        ),
        ActionSpace(
            space_id="chance_22",
            space_index=22,
            name="Chance",
            action="draw_chance"
        ),
        PropertySpace(
            space_id="indiana_avenue",
            space_index=23,
            name="Indiana Avenue",
            purchase_price=220,
            mortgage_value=110
        ),
        PropertySpace(
            space_id="illinois_avenue",
            space_index=24,
            name="Illinois Avenue",
            purchase_price=240,
            mortgage_value=120
        ),
        PropertySpace(
            space_id="b_and_o_railroad",
            space_index=25,
            name="B. & O. Railroad",
            purchase_price=200,
            mortgage_value=100
        ),
        PropertySpace(
            space_id="atlantic_avenue",
            space_index=26,
            name="Atlantic Avenue",
            purchase_price=260,
            mortgage_value=130
        ),
        PropertySpace(
            space_id="ventnor_avenue",
            space_index=27,
            name="Ventnor Avenue",
            purchase_price=260,
            mortgage_value=130
        ),
        PropertySpace(
            space_id="water_works",
            space_index=28,
            name="Water Works",
            purchase_price=150,
            mortgage_value=75
        ),
        PropertySpace(
            space_id="marvin_gardens",
            space_index=29,
            name="Marvin Gardens",
            purchase_price=280,
            mortgage_value=140
        ),
        ActionSpace(
            space_id="go_to_jail",
            space_index=30,
            name="Go To Jail",
            action="go_to_jail"
        ),
        PropertySpace(
            space_id="pacific_avenue",
            space_index=31,
            name="Pacific Avenue",
            purchase_price=300,
            mortgage_value=150
        ),
        PropertySpace(
            space_id="north_carolina_avenue",
            space_index=32,
            name="North Carolina Avenue",
            purchase_price=300,
            mortgage_value=150
        ),
        ActionSpace(
            space_id="community_chest_33",
            space_index=33,
            name="Community Chest",
            action="draw_chest"
        ),
        PropertySpace(
            space_id="pennsylvania_avenue",
            space_index=34,
            name="Pennsylvania Avenue",
            purchase_price=320,
            mortgage_value=160
        ),
        PropertySpace(
            space_id="short_line_railroad",
            space_index=35,
            name="Short Line Railroad",
            purchase_price=200,
            mortgage_value=100
        ),
        ActionSpace(
            space_id="chance_36",
            space_index=36,
            name="Chance",
            action="draw_chance"
        ),
        PropertySpace(
            space_id="park_place",
            space_index=37,
            name="Park Place",
            purchase_price=350,
            mortgage_value=175
        ),
        ActionSpace(
            space_id="luxury_tax",
            space_index=38,
            name="Luxury Tax",
            action="tax"
        ),
        PropertySpace(
            space_id="boardwalk",
            space_index=39,
            name="Boardwalk",
            purchase_price=400,
            mortgage_value=200
        )
    ]
)
