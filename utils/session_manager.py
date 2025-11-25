import sqlite3
from typing import Any, Optional, Dict, Literal
import json
from pathlib import Path


class SessionManager:
    def __init__(self, persist_path: str = "sessions.db", logger: Optional[Any] = None):
        self.persist_path = persist_path
        self.conn = sqlite3.connect(self.persist_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_db()
        self.logger = logger

    def log(self, level: Literal["INFO", "ERROR"], text: str) -> None:
        if self.logger:
            custom_logger = getattr(self.logger, level.lower(), None)
            if callable(custom_logger):
                custom_logger(text)
                return
        print(f"[{level}] {text}")

    def _initialize_db(self):
        """Initialize the database tables if they do not exist."""

        Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create users table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            data TEXT
        )
        """)

        # Create sessions table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            state TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        self.conn.commit()
    
    def get_user_data(self, user_id: str) -> Dict:
        """Get user data by user_id."""
        self.cursor.execute(
            "SELECT data FROM users WHERE user_id = ?",
            (user_id,)
        )
        data = self.cursor.fetchone()
        try:
            return json.loads(data[0]) if data else {}
        except (json.JSONDecodeError, IndexError):
            self.log("ERROR", f"Failed to decode user data for user_id: {user_id}")
            return {}
    
    def create_user(self, user_id: str) -> None:
        """Create a new user with the given user_id."""
        self.cursor.execute(
            "INSERT INTO users (user_id, data) VALUES (?, ?)",
            (user_id, json.dumps({'exists': True}))
        )
        self.conn.commit()
        self.log("INFO", f"Created new user: {user_id}")
    
    def create_session(self, user_id: str, session_id: str, state: Dict) -> None:
        """Create a new session with the given session_id, user_id, and state."""
        self.cursor.execute(
            "INSERT INTO sessions (session_id, user_id, state) VALUES (?, ?, ?)",
            (session_id, user_id, json.dumps(state))
        )
        self.conn.commit()
        self.log("INFO", f"Created new session: {session_id} for user: {user_id}")
    
    def get_session_state(self, user_id: str, session_id: Optional[str] = None) -> Dict:
        """Get the state of a session by user_id and session_id, or latest session if no session_id provided."""
        if session_id:
            # Fetch by user_id and session_id
            self.cursor.execute(
                "SELECT state FROM sessions WHERE session_id = ? AND user_id = ?",
                (session_id, user_id)
            )
        else:
            # Fetch latest session by user_id
            self.cursor.execute(
                "SELECT state FROM sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )

        result = self.cursor.fetchone()
        try:
            return json.loads(result[0]) if result else {}
        except (json.JSONDecodeError, IndexError):
            self.log("ERROR", f"Failed to decode session state for user_id: {user_id}, session_id: {session_id}")
            return {}

    def initialize_session(self, user_id: str, session_id: str) -> Dict:
        """Fetch the latest session state, create a new session with that state, return state."""
        latest_state = self.get_session_state(user_id) if user_id else {}
        self.create_session(user_id, session_id, latest_state)
        self.log("INFO", f"Initialized session: {session_id} for user: {user_id}")
        return latest_state

    def get_or_create_user(self, user_id: str) -> Dict:
        """Get existing user data or create a new user."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            self.create_user(user_id)
        return user_data
    
    def save(self, user_id: str, session_id: str, state: Dict) -> None:
        """Save the state of a session by user_id and session_id."""
        self.cursor.execute(
            "REPLACE INTO sessions (session_id, user_id, state) VALUES (?, ?, ?)",
            (session_id, user_id, json.dumps(state))
        )
        self.conn.commit()
        self.log("INFO", f"Saved state for session: {session_id} of user: {user_id}")
