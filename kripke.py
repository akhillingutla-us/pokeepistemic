"""
Kripke Model Engine for PokéEpistemic
Handles possible worlds, knowledge operators, and public announcement updates.
"""

from dataclasses import dataclass, field
from typing import Set, Dict, List, Any, Callable
from copy import deepcopy


@dataclass
class World:
    """A possible world representing an opponent's Pokemon configuration."""
    id: str
    pokemon: str
    moveset: Set[str]
    item: str
    ability: str
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return self.id == other.id
    
    def satisfies(self, proposition: str) -> bool:
        """Check if this world satisfies a proposition.
        
        Propositions can be:
        - "has_move:Earthquake" -> checks if move is in moveset
        - "has_item:Focus Sash" -> checks if item matches
        - "has_ability:Rough Skin" -> checks if ability matches
        """
        if proposition.startswith("has_move:"):
            move = proposition.split(":", 1)[1]
            return move in self.moveset
        elif proposition.startswith("has_item:"):
            item = proposition.split(":", 1)[1]
            return self.item == item
        elif proposition.startswith("has_ability:"):
            ability = proposition.split(":", 1)[1]
            return self.ability == ability
        elif proposition.startswith("not_has_move:"):
            move = proposition.split(":", 1)[1]
            return move not in self.moveset
        elif proposition.startswith("not_has_item:"):
            item = proposition.split(":", 1)[1]
            return self.item != item
        else:
            raise ValueError(f"Unknown proposition format: {proposition}")
    
    def __repr__(self):
        moves = ", ".join(sorted(self.moveset))
        return f"{self.pokemon}[{moves} | {self.item} | {self.ability}]"


class KripkeModel:
    """Kripke model for tracking epistemic state about opponent's Pokemon."""
    
    def __init__(self):
        self.worlds: Set[World] = set()
        self.eliminated: Set[World] = set()
    
    def add_world(self, world: World):
        """Add a possible world to the model."""
        self.worlds.add(world)
    
    def add_worlds_from_pokemon_data(self, pokemon: str, sets: List[Dict]):
        """Generate worlds from Pokemon set data.
        
        Args:
            pokemon: Pokemon name (e.g., "Garchomp")
            sets: List of possible sets, each with 'moves', 'item', 'ability'
        """
        for i, poke_set in enumerate(sets):
            world = World(
                id=f"{pokemon}_{i}",
                pokemon=pokemon,
                moveset=set(poke_set["moves"]),
                item=poke_set["item"],
                ability=poke_set["ability"]
            )
            self.add_world(world)
    
    def public_announcement(self, proposition: str) -> int:
        """Perform a public announcement update [!φ].
        
        Eliminates all worlds where the proposition is false.
        Returns the number of worlds eliminated.
        """
        to_eliminate = set()
        for world in self.worlds:
            if not world.satisfies(proposition):
                to_eliminate.add(world)
        
        self.worlds -= to_eliminate
        self.eliminated |= to_eliminate
        return len(to_eliminate)
    
    def knows(self, proposition: str) -> bool:
        """Evaluate K(φ) - do we know the proposition is true?
        
        Returns True iff φ is true in ALL remaining possible worlds.
        """
        if not self.worlds:
            return True  
        
        return all(world.satisfies(proposition) for world in self.worlds)
    
    def possibly(self, proposition: str) -> bool:
        """Evaluate ◇φ - is the proposition possibly true?
        
        Returns True iff φ is true in at least ONE remaining world.
        """
        return any(world.satisfies(proposition) for world in self.worlds)
    
    def get_known_moves(self) -> Set[str]:
        """Get moves that we KNOW the opponent has (true in all worlds)."""
        if not self.worlds:
            return set()
        
        known = None
        for world in self.worlds:
            if known is None:
                known = set(world.moveset)
            else:
                known &= world.moveset
        return known or set()
    
    def get_possible_moves(self) -> Set[str]:
        """Get all moves the opponent MIGHT have (true in at least one world)."""
        possible = set()
        for world in self.worlds:
            possible |= world.moveset
        return possible
    
    def get_possible_items(self) -> Set[str]:
        """Get all items the opponent might have."""
        return {world.item for world in self.worlds}
    
    def get_known_item(self) -> str | None:
        """Get the item if we know it for certain, else None."""
        items = self.get_possible_items()
        if len(items) == 1:
            return items.pop()
        return None
    
    def probability(self, proposition: str) -> float:
        """Estimate probability of a proposition (uniform distribution over worlds)."""
        if not self.worlds:
            return 0.0
        
        count = sum(1 for w in self.worlds if w.satisfies(proposition))
        return count / len(self.worlds)
    
    def __len__(self):
        return len(self.worlds)
    
    def status(self) -> str:
        """Get a summary of current epistemic state."""
        lines = [
            f"Possible worlds: {len(self.worlds)}",
            f"Eliminated worlds: {len(self.eliminated)}",
            f"Known moves: {self.get_known_moves() or 'None yet'}",
            f"Possible moves: {self.get_possible_moves()}",
            f"Possible items: {self.get_possible_items()}",
        ]
        known_item = self.get_known_item()
        if known_item:
            lines.append(f"Known item: {known_item}")
        return "\n".join(lines)

if __name__ == "__main__":
    model = KripkeModel()
    garchomp_sets = [
        {"moves": ["Earthquake", "Dragon Claw", "Swords Dance", "Scale Shot"], 
         "item": "Focus Sash", "ability": "Rough Skin"},
        {"moves": ["Earthquake", "Dragon Claw", "Fire Fang", "Stealth Rock"], 
         "item": "Rocky Helmet", "ability": "Rough Skin"},
        {"moves": ["Earthquake", "Outrage", "Swords Dance", "Stone Edge"], 
         "item": "Life Orb", "ability": "Rough Skin"},
    ]
    
    model.add_worlds_from_pokemon_data("Garchomp", garchomp_sets)
    
    print("=== Initial State ===")
    print(model.status())
    print(f"\nK(has_move:Earthquake)? {model.knows('has_move:Earthquake')}")
    print(f"K(has_move:Swords Dance)? {model.knows('has_move:Swords Dance')}")
    
    print("\n=== Observation: Garchomp used Swords Dance ===")
    eliminated = model.public_announcement("has_move:Swords Dance")
    print(f"Eliminated {eliminated} worlds")
    print(model.status())
    
    print(f"\nK(has_move:Swords Dance)? {model.knows('has_move:Swords Dance')}")
    print(f"K(has_item:Focus Sash)? {model.knows('has_item:Focus Sash')}")
    print(f"P(has_item:Focus Sash) = {model.probability('has_item:Focus Sash'):.0%}")
