# PokéEpistemic

**Modeling Hidden Information in Pokémon Battles with Dynamic Epistemic Logic**

A tool that formalizes the epistemic reasoning competitive Pokémon players do intuitively, using Kripke semantics and Dynamic Epistemic Logic (DEL).

## Overview

In competitive Pokémon, you face massive uncertainty—your opponent's movesets, items, and abilities are hidden. As the battle progresses, information is revealed through observations. This project models that reasoning formally:

- **Possible Worlds** = Different opponent configurations (from Smogon sets)
- **Public Announcements** = Observations that eliminate impossible worlds
- **Knowledge Operator K(φ)** = True only if φ holds in ALL remaining worlds

## Installation

```bash
git clone https://github.com/USERNAME/pokeepistemic.git
cd pokeepistemic
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Commands

| Command | Description |
|---------|-------------|
| `reveal <pokemon>` | Opponent sends out a Pokémon |
| `move <pokemon> <move>` | Observe a move being used |
| `item <pokemon> <item>` | Observe an item (activated/revealed) |
| `know move <pokemon> <move>` | Query: Do we KNOW they have this move? |
| `know item <pokemon> <item>` | Query: Do we KNOW they have this item? |
| `status` | Show current epistemic state |
| `history` | Show observation log |

### Example Session

```
>>> reveal dragapult
✓ Dragapult revealed! Initialized with 4 possible sets.

>>> move dragapult shadow ball
✓ Observed: Dragapult used Shadow Ball
  Eliminated 2 world(s)

>>> know item dragapult choice specs
=== Query: Does Dragapult have Choice Specs? ===
  K(Choice Specs): NO - We don't know for certain
  ◇(Choice Specs): YES - It's possible (50% of remaining sets)
```

## How It Works

### Kripke Model

Each Pokémon's possible configurations form a Kripke model:
- **W** (Worlds): Each competitive set is a possible world
- **V** (Valuation): Maps propositions like `has_move:Earthquake` to truth values
- **R** (Accessibility): Initially all worlds are accessible

### Public Announcement Update

When you observe something (e.g., opponent uses Swords Dance):
```
[!φ]ψ : W' = {w ∈ W | w ⊨ φ}
```
All worlds where the observation would be impossible are eliminated.

### Knowledge Evaluation

```
K(φ) is TRUE iff ∀w' ∈ W: w' ⊨ φ
```
You "know" something only if it's true in ALL remaining possible worlds.

## Project Structure

```
pokeepistemic/
├── main.py           # CLI interface
├── kripke.py         # Kripke model engine
├── pokemon_data.py   # Smogon Gen9 OU sets (23 Pokémon, 62 sets)
├── visualize.py      # NetworkX visualization
├── requirements.txt
└── README.md
```

## Supported Pokémon

Data sourced from [Smogon Gen9 OU](https://pkmn.github.io/smogon/data/sets/):

Garchomp, Dragapult, Gholdengo, Kingambit, Great Tusk, Iron Valiant, Rillaboom, Heatran, Landorus-Therian, Kyurem, Darkrai, Dragonite, Raging Bolt, Ting-Lu, Ogerpon-Wellspring, Gliscor, Corviknight, Toxapex, Weavile, Skeledirge, Zamazenta, Meowscarada, Iron Crown

## Visualization

Generate Kripke model diagrams:

```bash
python visualize.py #pokémonName
```

This creates PNG files showing:
- **Worlds (w1–w4)**  
  Each world corresponds to a *possible Dragapult build*, defined by a specific item and role:
  - Choice Specs: special attacker (e.g., Draco Meteor, Flamethrower, Shadow Ball)
  - Choice Band: physical attacker (e.g., Dragon Darts, Sucker Punch, U-turn)
  - Life Orb: mixed attacker with broad coverage
  - Heavy-Duty Boots: pivot or utility variant

- **Valuations (V)**  
  The propositions listed inside each node are the properties that are true if that world is the actual one, such as Dragapult’s item and available moves.

- **Accessibility Relation (R)**  
  All worlds are mutually accessible, meaning that from the player’s current knowledge, every Dragapult set is still possible.

- **Gameplay Meaning**  
  Before Dragapult reveals a move, item, or damage output, the player cannot rule out any of these builds. The model captures this initial state of complete uncertainty.

As the battle progresses and Dragapult reveals information (for example, using a physical move or avoiding hazard damage), some worlds would be eliminated, reducing the set of possible worlds.

## References

- van Ditmarsch, H., van der Hoek, W., & Kooi, B. (2007). *Dynamic Epistemic Logic*. Cambridge University Press.
- Smogon University. Gen9 OU Sets. https://www.smogon.com/dex/sv/formats/ou/

## License

MIT
