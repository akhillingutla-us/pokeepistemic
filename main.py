"""
PokéEpistemic: Modeling Hidden Information in Pokemon Battles
Main CLI Interface
"""

from kripke import KripkeModel, World
from pokemon_data import fetch_smogon_data, get_pokemon_names, get_sets, get_all_moves, get_all_items


class BattleTracker:
    """Track epistemic state for opponent's Pokemon during a battle."""
    
    def __init__(self):
        self.pokemon_models: dict[str, KripkeModel] = {}
        self.revealed_pokemon: list[str] = []
        self.observations: list[str] = []
    
    def reveal_pokemon(self, pokemon: str) -> bool:
        """Opponent reveals a Pokemon. Initialize its Kripke model."""
        pokemon = self._normalize_name(pokemon)
        
        if pokemon not in fetch_smogon_data():
            print(f"Unknown Pokemon: {pokemon}")
            print(f"Available: {', '.join(get_pokemon_names())}")
            return False
        
        if pokemon in self.pokemon_models:
            print(f"{pokemon} already revealed.")
            return False
        
        model = KripkeModel()
        model.add_worlds_from_pokemon_data(pokemon, get_sets(pokemon))
        
        self.pokemon_models[pokemon] = model
        self.revealed_pokemon.append(pokemon)
        self.observations.append(f"Opponent sent out {pokemon}")
        
        print(f"\n✓ {pokemon} revealed! Initialized with {len(model)} possible sets.")
        self._print_pokemon_status(pokemon)
        return True
    
    def observe_move(self, pokemon: str, move: str) -> bool:
        """Observe a Pokemon using a move. Updates Kripke model via public announcement."""
        pokemon = self._normalize_name(pokemon)
        move = self._normalize_move(move)
        
        if pokemon not in self.pokemon_models:
            print(f"{pokemon} not revealed yet. Use 'reveal {pokemon}' first.")
            return False
        
        model = self.pokemon_models[pokemon]
        proposition = f"has_move:{move}"
        
        if not model.possibly(proposition):
            print(f"⚠ {move} is not possible for any known {pokemon} set!")
            print(f"  This might be a non-standard set or typo.")
            return False
        
        eliminated = model.public_announcement(proposition)
        self.observations.append(f"{pokemon} used {move}")
        
        print(f"\n✓ Observed: {pokemon} used {move}")
        print(f"  Eliminated {eliminated} world(s)")
        self._print_pokemon_status(pokemon)
        return True
    
    def observe_item(self, pokemon: str, item: str) -> bool:
        """Observe a Pokemon's item being revealed."""
        pokemon = self._normalize_name(pokemon)
        item = self._normalize_item(item)
        
        if pokemon not in self.pokemon_models:
            print(f"{pokemon} not revealed yet.")
            return False
        
        model = self.pokemon_models[pokemon]
        proposition = f"has_item:{item}"
        
        if not model.possibly(proposition):
            print(f"⚠ {item} is not possible for any known {pokemon} set!")
            return False
        
        eliminated = model.public_announcement(proposition)
        self.observations.append(f"{pokemon}'s {item} was revealed")
        
        print(f"\n✓ Observed: {pokemon} has {item}")
        print(f"  Eliminated {eliminated} world(s)")
        self._print_pokemon_status(pokemon)
        return True
    
    def observe_no_item(self, pokemon: str, item: str) -> bool:
        """Observe that a Pokemon does NOT have a specific item."""
        pokemon = self._normalize_name(pokemon)
        item = self._normalize_item(item)
        
        if pokemon not in self.pokemon_models:
            print(f"{pokemon} not revealed yet.")
            return False
        
        model = self.pokemon_models[pokemon]
        proposition = f"not_has_item:{item}"
        
        eliminated = model.public_announcement(proposition)
        self.observations.append(f"{pokemon} does not have {item}")
        
        print(f"\n✓ Observed: {pokemon} does NOT have {item}")
        print(f"  Eliminated {eliminated} world(s)")
        self._print_pokemon_status(pokemon)
        return True
    
    def query_move(self, pokemon: str, move: str):
        """Query: Do we KNOW the opponent has this move? Evaluates K(has_move:X)."""
        pokemon = self._normalize_name(pokemon)
        move = self._normalize_move(move)
        
        if pokemon not in self.pokemon_models:
            print(f"{pokemon} not revealed yet.")
            return
        
        model = self.pokemon_models[pokemon]
        prop = f"has_move:{move}"
        
        knows = model.knows(prop)
        possibly = model.possibly(prop)
        prob = model.probability(prop)
        
        print(f"\n=== Query: Does {pokemon} have {move}? ===")
        if knows:
            print(f"  K({move}): YES - We KNOW they have it (100%)")
        elif possibly:
            print(f"  K({move}): NO - We don't know for certain")
            print(f"  ◇({move}): YES - It's possible ({prob:.0%} of remaining sets)")
        else:
            print(f"  K(¬{move}): YES - We KNOW they DON'T have it (0%)")
    
    def query_item(self, pokemon: str, item: str):
        """Query: Do we KNOW the opponent has this item? Evaluates K(has_item:X)."""
        pokemon = self._normalize_name(pokemon)
        item = self._normalize_item(item)
        
        if pokemon not in self.pokemon_models:
            print(f"{pokemon} not revealed yet.")
            return
        
        model = self.pokemon_models[pokemon]
        prop = f"has_item:{item}"
        
        knows = model.knows(prop)
        possibly = model.possibly(prop)
        prob = model.probability(prop)
        
        print(f"\n=== Query: Does {pokemon} have {item}? ===")
        if knows:
            print(f"  K({item}): YES - We KNOW they have it (100%)")
        elif possibly:
            print(f"  K({item}): NO - We don't know for certain")
            print(f"  ◇({item}): YES - It's possible ({prob:.0%} of remaining sets)")
        else:
            print(f"  K(¬{item}): YES - We KNOW they DON'T have it (0%)")
    
    def status(self, pokemon: str = None):
        """Print current epistemic status for all or specific Pokemon."""
        if pokemon:
            pokemon = self._normalize_name(pokemon)
            if pokemon in self.pokemon_models:
                self._print_pokemon_status(pokemon)
            else:
                print(f"{pokemon} not revealed yet.")
        else:
            print("\n" + "="*50)
            print("BATTLE STATUS")
            print("="*50)
            if not self.revealed_pokemon:
                print("No Pokemon revealed yet.")
            for poke in self.revealed_pokemon:
                self._print_pokemon_status(poke)
    
    def _print_pokemon_status(self, pokemon: str):
        model = self.pokemon_models[pokemon]
        
        print(f"\n--- {pokemon} ---")
        print(f"Possible sets remaining: {len(model)}")
        
        known_moves = model.get_known_moves()
        if known_moves:
            print(f"Known moves: {', '.join(sorted(known_moves))}")
        
        possible_moves = model.get_possible_moves() - known_moves
        if possible_moves:
            print(f"Possible moves: {', '.join(sorted(possible_moves))}")
        
        known_item = model.get_known_item()
        if known_item:
            print(f"Known item: {known_item}")
        else:
            possible_items = model.get_possible_items()
            print(f"Possible items: {', '.join(sorted(possible_items))}")
        
        if len(model) <= 4:
            print("Remaining possible sets:")
            for world in model.worlds:
                print(f"  • {world}")
    
    def history(self):
        """Print observation history."""
        print("\n=== Observation History ===")
        for i, obs in enumerate(self.observations, 1):
            print(f"{i}. {obs}")
    
    def _normalize_name(self, name: str) -> str:
        name = name.strip().title()
        if name.lower() == "flutter mane" or name.lower() == "fluttermane":
            return "Flutter Mane"
        if name.lower() == "great tusk" or name.lower() == "greattusk":
            return "Great Tusk"
        if name.lower() == "iron valiant" or name.lower() == "ironvaliant":
            return "Iron Valiant"
        if "urshifu" in name.lower():
            return "Urshifu-Rapid"
        return name
    
    def _normalize_move(self, move: str) -> str:
        return move.strip().title()
    
    def _normalize_item(self, item: str) -> str:
        return item.strip().title()


def print_help():
    """Print available commands."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    PokéEpistemic Commands                    ║
╠══════════════════════════════════════════════════════════════╣
║  reveal <pokemon>         - Opponent sends out a Pokemon     ║
║  move <pokemon> <move>    - Observe a move being used        ║
║  item <pokemon> <item>    - Observe an item (activated/seen) ║
║  noitem <pokemon> <item>  - Pokemon definitely lacks item    ║
║                                                              ║
║  know move <pokemon> <move>  - Query: K(has move)?           ║
║  know item <pokemon> <item>  - Query: K(has item)?           ║
║                                                              ║
║  status [pokemon]         - Show epistemic state             ║
║  history                  - Show observation log             ║
║  pokemon                  - List available Pokemon           ║
║  help                     - Show this help                   ║
║  quit                     - Exit                             ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                      PokéEpistemic                        ║
    ║     Modeling Hidden Information with Epistemic Logic      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print("Type 'help' for commands, 'pokemon' to see available Pokemon.\n")
    
    tracker = BattleTracker()
    
    while True:
        try:
            cmd = input(">>> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not cmd:
            continue
        
        parts = cmd.split()
        action = parts[0]
        
        if action == "quit" or action == "exit" or action == "q":
            print("Goodbye!")
            break
        
        elif action == "help" or action == "h" or action == "?":
            print_help()
        
        elif action == "pokemon" or action == "list":
            print("\nAvailable Pokemon:")
            for poke in get_pokemon_names():
                sets = get_sets(poke)
                print(f"  • {poke} ({len(sets)} sets)")
        
        elif action == "reveal":
            if len(parts) < 2:
                print("Usage: reveal <pokemon>")
            else:
                pokemon = " ".join(parts[1:])
                tracker.reveal_pokemon(pokemon)
        
        elif action == "move":
            if len(parts) < 3:
                print("Usage: move <pokemon> <move>")
            else:
                pokemon = parts[1]
                move = " ".join(parts[2:])
                tracker.observe_move(pokemon, move)
        
        elif action == "item":
            if len(parts) < 3:
                print("Usage: item <pokemon> <item>")
            else:
                pokemon = parts[1]
                item = " ".join(parts[2:])
                tracker.observe_item(pokemon, item)
        
        elif action == "noitem":
            if len(parts) < 3:
                print("Usage: noitem <pokemon> <item>")
            else:
                pokemon = parts[1]
                item = " ".join(parts[2:])
                tracker.observe_no_item(pokemon, item)
        
        elif action == "know":
            if len(parts) < 4:
                print("Usage: know move <pokemon> <move>")
                print("       know item <pokemon> <item>")
            elif parts[1] == "move":
                pokemon = parts[2]
                move = " ".join(parts[3:])
                tracker.query_move(pokemon, move)
            elif parts[1] == "item":
                pokemon = parts[2]
                item = " ".join(parts[3:])
                tracker.query_item(pokemon, item)
        
        elif action == "status":
            if len(parts) > 1:
                tracker.status(" ".join(parts[1:]))
            else:
                tracker.status()
        
        elif action == "history":
            tracker.history()
        
        else:
            print(f"Unknown command: {action}. Type 'help' for commands.")


if __name__ == "__main__":
    main()