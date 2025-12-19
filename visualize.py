"""
Visualization for PokéEpistemic Kripke Models
Renders proper Kripke structures with accessibility relations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle
from kripke import KripkeModel, World
from typing import Optional
import math


def visualize_model(model: KripkeModel, pokemon: str, title: str = None, 
                    save_path: Optional[str] = None):
    
    remaining = list(model.worlds)
    eliminated = list(model.eliminated)
    all_worlds = remaining + eliminated
    
    if len(all_worlds) == 0:
        print("No worlds to visualize.")
        return
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    
    n = len(all_worlds)
    positions = {}
    radius = 0.13
    
    if n == 1:
        positions[all_worlds[0].id] = (0.5, 0.5)
    elif n == 2:
        positions[all_worlds[0].id] = (0.28, 0.5)
        positions[all_worlds[1].id] = (0.72, 0.5)
    elif n == 3:
        positions[all_worlds[0].id] = (0.5, 0.78)
        positions[all_worlds[1].id] = (0.22, 0.32)
        positions[all_worlds[2].id] = (0.78, 0.32)
    elif n == 4:
        positions[all_worlds[0].id] = (0.22, 0.72)
        positions[all_worlds[1].id] = (0.78, 0.72)
        positions[all_worlds[2].id] = (0.22, 0.28)
        positions[all_worlds[3].id] = (0.78, 0.28)
    else:
        for i, world in enumerate(all_worlds):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = 0.5 + 0.3 * math.cos(angle)
            y = 0.5 + 0.3 * math.sin(angle)
            positions[world.id] = (x, y)
    
    for i, w1 in enumerate(remaining):
        for j, w2 in enumerate(remaining):
            if i < j:
                x1, y1 = positions[w1.id]
                x2, y2 = positions[w2.id]
                
                dx, dy = x2 - x1, y2 - y1
                dist = math.sqrt(dx*dx + dy*dy)
                
                start_x = x1 + radius * dx / dist
                start_y = y1 + radius * dy / dist
                end_x = x2 - radius * dx / dist
                end_y = y2 - radius * dy / dist
                
                arrow = FancyArrowPatch(
                    (start_x, start_y), (end_x, end_y),
                    arrowstyle='<->', 
                    mutation_scale=15,
                    color='#333333',
                    linewidth=1.5,
                    connectionstyle='arc3,rad=0.1'
                )
                ax.add_patch(arrow)
    
    for world in remaining:
        x, y = positions[world.id]
        if len(remaining) == 1:
            loop = FancyArrowPatch(
                (x + radius, y + 0.02), (x + radius, y - 0.02),
                arrowstyle='->',
                mutation_scale=12,
                color='#333333',
                linewidth=1.5,
                connectionstyle='arc3,rad=-2.5'
            )
            ax.add_patch(loop)
    
    for i, world in enumerate(eliminated):
        x, y = positions[world.id]
        circle = Circle((x, y), radius, color='#ffcccc', ec='#cc9999', 
                        linewidth=2, alpha=0.5, zorder=10)
        ax.add_patch(circle)
        
        state_label = f"w{i + len(remaining) + 1}"
        ax.text(x, y + radius + 0.02, state_label, ha='center', va='bottom', 
                fontsize=12, color='#999999', fontstyle='italic', zorder=20)
        ax.text(x, y, _format_props(world), ha='center', va='center', 
                fontsize=8, color='#666666', zorder=20)
    
    for i, world in enumerate(remaining):
        x, y = positions[world.id]
        circle = Circle((x, y), radius, color='#90EE90', ec='#228B22', 
                        linewidth=2.5, zorder=10)
        ax.add_patch(circle)
        
        state_label = f"w{i + 1}"
        ax.text(x, y + radius + 0.02, state_label, ha='center', va='bottom', 
                fontsize=13, color='#000000', fontweight='bold', zorder=20)
        ax.text(x, y, _format_props(world), ha='center', va='center', 
                fontsize=8, color='#000000', zorder=20)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    else:
        ax.set_title(f"{pokemon} - Kripke Model M = (W, R, V)\n"
                     f"W = {{{', '.join(f'w{i+1}' for i in range(len(remaining)))}}}, "
                     f"R = universal on W",
                     fontsize=12, fontweight='bold', pad=20)
    
    green_patch = mpatches.Patch(color='#90EE90', ec='#228B22', 
                                  label=f'Accessible worlds ({len(remaining)})')
    red_patch = mpatches.Patch(color='#ffcccc', ec='#cc9999',
                                label=f'Eliminated ({len(eliminated)})')
    ax.legend(handles=[green_patch, red_patch], loc='upper right', fontsize=10)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved visualization to {save_path}")
        plt.close()
    else:
        plt.show()


def _format_props(world: World) -> str:
    item = world.item if len(world.item) <= 14 else world.item[:12] + ".."
    moves = sorted(world.moveset)
    move_abbrev = []
    for m in moves:
        if len(m) > 8:
            move_abbrev.append(m[:6] + "..")
        else:
            move_abbrev.append(m)
    line1 = ", ".join(move_abbrev[:2])
    line2 = ", ".join(move_abbrev[2:]) if len(move_abbrev) > 2 else ""
    if line2:
        return f"{item}\n{line1}\n{line2}"
    return f"{item}\n{line1}"


if __name__ == "__main__":
    import sys
    from pokemon_data import get_sets, get_pokemon_names
    
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <pokemon> [move_to_observe]")
        print(f"\nAvailable Pokemon: {', '.join(get_pokemon_names()[:10])}...")
        print("\nExample: python visualize.py Dragapult")
        print("         python visualize.py Garchomp 'Swords Dance'")
        sys.exit(1)
    
    pokemon = sys.argv[1]
    move = sys.argv[2] if len(sys.argv) > 2 else None
    
    sets = get_sets(pokemon)
    if not sets:
        print(f"Pokemon '{pokemon}' not found.")
        sys.exit(1)
    
    model = KripkeModel()
    model.add_worlds_from_pokemon_data(pokemon, sets)
    
    filename = pokemon.lower().replace(" ", "_").replace("-", "_")
    
    print(f"=== {pokemon}: Initial State ===")
    visualize_model(model, pokemon, save_path=f"{filename}_initial.png")
    
    if move:
        print(f"\n=== After observing {move} ===")
        eliminated = model.public_announcement(f"has_move:{move}")
        print(f"Eliminated {eliminated} world(s)")
        visualize_model(model, pokemon, save_path=f"{filename}_after.png")