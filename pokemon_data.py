"""
Pokemon Competitive Sets Database
Fetches real time data from Smogon through pkmn.github.io API

Data Source: https://pkmn.github.io/smogon/data/sets/
"""

import json
import urllib.request
from typing import Optional

SMOGON_API_URL = "https://data.pkmn.cc/sets/gen9ou.json"

_CACHE: dict = {}


def fetch_smogon_data() -> dict:
    """Fetch Smogon sets data from the API.
    
    returns cached data if available, fetches from API otherwise.
    """
    if "data" in _CACHE:
        return _CACHE["data"]
    
    print("Fetching Smogon Gen9 OU data...")
    try:
        req = urllib.request.Request(
            SMOGON_API_URL,
            headers={"User-Agent": "PokeEpistemic/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            _CACHE["data"] = data
            print(f"✓ Loaded {len(data)} Pokemon from Smogon")
            return data
    except Exception as e:
        print(f"Error fetching Smogon data: {e}")
        print("Using minimal fallback data...")
        return _get_fallback_data()


def _get_fallback_data() -> dict:
    """Minimal fallback if API is unavailable."""
    return {
        "Garchomp": {
            "TankChomp": {"moves": ["Earthquake", "Dragon Tail", "Stealth Rock", "Spikes"], "ability": "Rough Skin", "item": "Rocky Helmet"},
            "Swords Dance": {"moves": ["Swords Dance", "Scale Shot", "Earthquake", "Fire Fang"], "ability": "Rough Skin", "item": "Loaded Dice"}
        },
        "Dragapult": {
            "Choice Specs": {"moves": ["Draco Meteor", "Shadow Ball", "Flamethrower", "U-turn"], "ability": "Infiltrator", "item": "Choice Specs"},
            "Choice Band": {"moves": ["Dragon Darts", "Tera Blast", "U-turn", "Sucker Punch"], "ability": "Clear Body", "item": "Choice Band"}
        }
    }


def get_pokemon_names() -> list[str]:
    """Get list of all Pokemon in the database."""
    data = fetch_smogon_data()
    return list(data.keys())


def get_sets(pokemon: str) -> list[dict]:
    """Get all competitive sets for a Pokemon.
    
    Handles Smogon's "slash notation" where moves/items can be lists of options.
    We take the first option from each slot to create concrete sets.
    
    Returns list of dicts with: name, moves, item, ability
    """
    data = fetch_smogon_data()
    pokemon_data = data.get(pokemon, {})
    
    sets = []
    for set_name, set_data in pokemon_data.items():
        moves = _flatten_options(set_data.get("moves", []))
        item = _get_first(set_data.get("item", "Unknown"))
        ability = _get_first(set_data.get("ability", "Unknown"))
        
        sets.append({
            "name": set_name,
            "moves": moves,
            "item": item,
            "ability": ability
        })
    
    return sets


def _flatten_options(moves: list) -> list[str]:
    """Flatten nested move lists (slash options) into concrete moveset.
    
    Smogon format: ["Move1", ["Move2", "Move3"], "Move4"]
    means Move2 and Move3 are interchangeable options.
    
    We take the FIRST option from each slot.
    """
    result = []
    for move in moves:
        if isinstance(move, list):
            result.append(move[0])
        else:
            result.append(move)
    return result


def _get_first(value) -> str:
    """Get first value if list, otherwise return as-is."""
    if isinstance(value, list):
        return value[0]
    return value


def get_all_moves(pokemon: str) -> set[str]:
    """Get ALL possible moves for a Pokemon (including all slash options)."""
    data = fetch_smogon_data()
    pokemon_data = data.get(pokemon, {})
    
    moves = set()
    for set_data in pokemon_data.values():
        for move in set_data.get("moves", []):
            if isinstance(move, list):
                moves.update(move)
            else:
                moves.add(move)
    return moves


def get_all_items(pokemon: str) -> set[str]:
    """Get all possible items for a Pokemon across all sets."""
    data = fetch_smogon_data()
    pokemon_data = data.get(pokemon, {})
    
    items = set()
    for set_data in pokemon_data.values():
        item = set_data.get("item", "Unknown")
        if isinstance(item, list):
            items.update(item)
        else:
            items.add(item)
    return items


def get_all_abilities(pokemon: str) -> set[str]:
    """Get all possible abilities for a Pokemon across all sets."""
    data = fetch_smogon_data()
    pokemon_data = data.get(pokemon, {})
    
    abilities = set()
    for set_data in pokemon_data.values():
        ability = set_data.get("ability", "Unknown")
        if isinstance(ability, list):
            abilities.update(ability)
        else:
            abilities.add(ability)
    return abilities


def search_pokemon(query: str) -> list[str]:
    """Search for Pokemon by partial name match."""
    data = fetch_smogon_data()
    query_lower = query.lower()
    return [name for name in data.keys() if query_lower in name.lower()]


if __name__ == "__main__":
    print("=== Pokemon Database (Smogon API) ===\n")
    
    data = fetch_smogon_data()
    total_sets = sum(len(sets) for sets in data.values())
    print(f"Total Pokemon: {len(data)}")
    print(f"Total Sets: {total_sets}\n")
    
    examples = ["Garchomp", "Dragapult", "Gholdengo", "Great Tusk", "Kingambit"]
    for pokemon in examples:
        if pokemon in data:
            sets = get_sets(pokemon)
            print(f"{pokemon}: {len(sets)} sets")
            for s in sets:
                print(f"  • {s['name']}: {s['item']}")
            print()