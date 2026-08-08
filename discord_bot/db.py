# Want to switch to postgress to learn eventually

import json
import sqlite3
from contextlib import closing

from diplo_engine import GameState

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    map_path TEXT NOT NULL,
    state_json TEXT NOT NULL,
    channel_id TEXT,
    status TEXT NOT NULL DEFAULT 'active'
);
 
CREATE TABLE IF NOT EXISTS players (
    game_id TEXT NOT NULL REFERENCES games(id),
    power TEXT NOT NULL,
    discord_user_id TEXT NOT NULL,
    PRIMARY KEY (game_id, power)
);
 
CREATE TABLE IF NOT EXISTS orders (
    game_id TEXT NOT NULL REFERENCES games(id),
    phase_key TEXT NOT NULL,
    power TEXT NOT NULL,
    unit_location TEXT NOT NULL,
    order_text TEXT NOT NULL,
    PRIMARY KEY (game_id, phase_key, unit_location)
);
 
CREATE TABLE IF NOT EXISTS phase_history (
    game_id TEXT NOT NULL REFERENCES games(id),
    phase_key TEXT NOT NULL,
    state_json TEXT NOT NULL,
    PRIMARY KEY (game_id, phase_key)
);
"""

class Storage:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path, chcek_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        with closing(self.conn.cursor()) as cur:
            cur.executescript(SCHEMA)
        self.conn.commit()

    def create_game(self, game_id: str, name: str, map_path: str, state: GameState, channel_id: str | None = None) -> None:
        self.conn.execute("INSERT INTO games (id, name, map_path, state_json, channel_id) VALUES (?,?,?,?,?)", (game_id, name, map_path, json.dump(state.to_dict()), channel_id),
                          )
        self.conn.commit()

    def load_state(self, game_id: str) -> GameState:
        row = self.conn.execute("SELECT state_json FROM games WHERE id=?", (game_id,)).fetchone()
        if row is None:
            raise KeyError(f"No such game: {game_id}")
        return GameState.from_dict(json.loads(row["state_json"]))

    # Overwrites the current state and uses the phase key that just completed.
    def save_state(self, game_id: str, phase_key_before: str, state: GameState) -> None:
        self.conn.execute("UPDATE games SET state_json=? WHERE id =?", (json.dumps(state.to_dict()), game_id), )
        self.conn.execute("INSERT OR REPLACE INTO phase_history (game_id, phase_key, state_json) VALUES (?,?,?)", (game_id, phase_key_before, json.dump(state.to_dict())), )
        self.conn.commit()

    def get_map_path(self, game_id: str) -> str:
        row = self.conn.execute("SELECT map_path FROM games WHERE id=?", (game_id,)).fetchone()
        if row is None:
            raise KeyError(f"No such game: {game_id}")
        return row["map_path"]

    def add_player(self, game_id: str, power: str, discord_user_id: str) -> None:
    self.conn.execute("INSERT OR REPLACE INTO players (game_id, power, discord_user_id) VALUES (?,?,?)",(game_id, power, discord_user_id), )
    self.conn.commit()

    # Should allow for multiple players to control one power... TODO: test
    def get_power_for_user(self, game_id: str, discord_user_id: str) -> str | None:
        row = self.conn.execute("SELECT power FROM players WHERE game_id=? AND discord_user_id=?", (game_id, discord_user_id),).fetchone()
        return row["power"] if row else None

    def submit_order(self, game_id: str, phase_key: str, power: str, unit_location: str, order_text: str) -> None:
        self.conn.execute("INSERT OR REPLACE INTO orders (game_id, phase_key, power, unit_location, order_text) VALUES (?,?,?,?,?)", (game_id, phase_key, power, unit_location, order_text), )
        self.conn.commit()
 
    def get_orders(self, game_id: str, phase_key: str) -> list[tuple[str, str, str]]:
        rows = self.conn.execute("SELECT power, unit_location, order_text FROM orders WHERE game_id=? AND phase_key=?", (game_id, phase_key), ).fetchall()
        return [(r["power"], r["unit_location"], r["order_text"]) for r in rows]
 
    def clear_orders(self, game_id: str, phase_key: str) -> None:
        self.conn.execute("DELETE FROM orders WHERE game_id=? AND phase_key=?", (game_id, phase_key))
        self.conn.commit()