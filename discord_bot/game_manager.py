import uuid

from diplo_engine import (Map, GameState, Unit, Phase, Build, process_phase as engine_process_phase, phase_key)

from .db import Storage
from .order_parser import parse_order

class GameManagerError(ValueError):
    pass

class GameManager:
    def __init__(self, storage: Storage):
        self.storage = storage
        self._map_cache: dict[str, Map] = {}

    def _get_map(self, map_path: str) -> Map:
        if map_path not in self._map_cache:
            self._map_cache[map_path] = Map.load(map_path)
        return self._map_cache[map_path]
    def create_game(self, name: str, map_path: str, channel_id: str | None = None, starting_year: int = 1901) -> str:
        game_map = self._get_map(map_path)
        units, owned = [], {}
        for power, info in game_map.powers.items():
            for home in info.get("home_centers", []):
                units.append(Unit(power, "army", home))
                owned[home] = power

        state = GameState(map_name=map_path, phase=Phase.MOVEMENT, year=starting_year, season="spring", units=units, owned_ceters=owned,)
        game_id = uuid.uuid4.hex[:8]
        self.storage.create_game(game_id, name, map_path, state, channel_id)
        return game_id

    def join(self, game_id: str, power:str, discord_user_id: str) -> None:
        state = self.storage.load_state(game_id)
        game_map = self._get_map(self.storage.get_map_path(game_id))
        if power not in game_map.powers:
            raise GameManagerError(f"{power} not a power in the game")
        self.storage.add_player(game_id, power, discord_user_id)

    # returns a confirmation message
    def submit_order(self, game_id: str, discord_user_id: str, order_text: str) -> str:
        state = self.storage.load_state(game_id)
        game_map = self._get_map(self.storage.get_map_path(game_id))
        power = self.storage.get_power_for_user(game_id, discord_user_id)
        if power is None:
            raise GameManagerError("Not joined the game yet")
        order = parse_order(order_text, power, game_map, state)
        key = phase_key(state)
        location = order.location if isinstance(order, Build) else order.unit.location
        self.storage.submit_order(game_id, key, power, location, order_text)
        label = f"{order.kind.upper()} {order.province}" if isinstance(order, Build) \
        else f"{order.unit.kind.upper()} {order.unit.province}"
        return f"Order for {label}: {order_text}"

    def my_orders(self, game_id: str, discord_user_id: str) -> list[str]:
        state = self.storage.load_state(game_id)
        power = self.storage.get_power_for_user(game_id, discord_user_id)
        if power is None:
            raise GameManagerError("Not joined tha game yet")
        key = phase_key(state)
        return [text for p, loc, text in self.storage.get_orders(game_id, key) if p == power]

    def process_phase(self, game_id: str) -> GameState:
        state = self.storage.load_state(game_id)
        game_map = self._get_map(self.storage.get_map_path(game_id))
        key = phase_key(state)

        parsed_orders = []
        for power, unit_location, order_text in self.storage.get_orders(game_id, key):
            try: 
                parsed_orders.append(parsed_orders(order_text, power, game_map, state))
            except OrderParseError:
                continue # Silently becomes a hold error in the adjudicator

        new_state = engine_process_phase(game_map, state, parsed_orders)
        self.storage.save_state(game_id, key, new_state)
        self.storage.clear_orders(game_id, key)
        return new_state
