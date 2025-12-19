"""
Visualization for PokéEpistemic Kripke Models
Uses NetworkX and Matplotlib to render possible worlds.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from kripke import KripkeModel, World
from typing import Optional


def visualize_model(model: KripkeModel, pokemon: str, title: str = None, 
                    save_path: Optional[str] = None):
    """
    Visualize a Kripke model showing remaining vs eliminated worlds.
    
    Args:
        model: The KripkeModel to visualize
        pokemon: Pokemon name for labeling
        title: Optional title for the graph
        save_path: If provided, save to this path instead of displaying
    """
    G = nx.Graph()

    for world in model.worlds:
        label = f"{world.item}\n{_format_moves(world.moveset)}"
        G.add_node(world.id, label=label, eliminated=False)
    
    for world in model.eliminated:
        label = f"{world.item}\n{_format_moves(world.moveset)}"
        G.add_node(world.id, label=label, eliminated=True)
    
    if len(G.nodes) == 0:
        print("No worlds to visualize.")
        return
    
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    remaining_nodes = [n for n, d in G.nodes(data=True) if not d['eliminated']]
    eliminated_nodes = [n for n, d in G.nodes(data=True) if d['eliminated']]

    if eliminated_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=eliminated_nodes, 
                               node_color='#ffcccc', node_size=3000,
                               alpha=0.5, ax=ax)

        elim_labels = {n: G.nodes[n]['label'] for n in eliminated_nodes}
        nx.draw_networkx_labels(G, pos, elim_labels, font_size=8, 
                                font_color='#999999', ax=ax)
    
    if remaining_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=remaining_nodes,
                               node_color='#90EE90', node_size=3000,
                               edgecolors='#228B22', linewidths=2, ax=ax)
        remain_labels = {n: G.nodes[n]['label'] for n in remaining_nodes}
        nx.draw_networkx_labels(G, pos, remain_labels, font_size=8,
                                font_color='#000000', ax=ax)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    else:
        ax.set_title(f"{pokemon} - Possible Worlds\n"
                     f"({len(remaining_nodes)} remaining, {len(eliminated_nodes)} eliminated)",
                     fontsize=14, fontweight='bold')
    
    green_patch = mpatches.Patch(color='#90EE90', label=f'Possible ({len(remaining_nodes)})')
    red_patch = mpatches.Patch(color='#ffcccc', label=f'Eliminated ({len(eliminated_nodes)})')
    ax.legend(handles=[green_patch, red_patch], loc='upper left')
    
    ax.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved visualization to {save_path}")
        plt.close()
    else:
        plt.show()


def _format_moves(moveset: set) -> str:
    """Format moveset for display (abbreviated)."""
    moves = sorted(moveset)
    abbrev = []
    for m in moves:
        if len(m) > 10:
            abbrev.append(m[:8] + "..")
        else:
            abbrev.append(m)

    lines = []
    for i in range(0, len(abbrev), 2):
        lines.append(", ".join(abbrev[i:i+2]))
    return "\n".join(lines)


def visualize_battle_sequence(pokemon: str, sets: list, observations: list[tuple],
                               save_prefix: str = None):
    """
    Generate a sequence of visualizations showing knowledge evolution.
    
    Args:
        pokemon: Pokemon name
        sets: List of set dictionaries
        observations: List of (type, value) tuples, e.g., ("move", "Swords Dance")
        save_prefix: If provided, save as {prefix}_0.png, {prefix}_1.png, etc.
    """
    from kripke import KripkeModel
    
    model = KripkeModel()
    model.add_worlds_from_pokemon_data(pokemon, sets)
    title = f"{pokemon}: Initial State ({len(model)} possible sets)"
    save_path = f"{save_prefix}_0.png" if save_prefix else None
    visualize_model(model, pokemon, title, save_path)
    
    for i, (obs_type, value) in enumerate(observations, 1):
        if obs_type == "move":
            prop = f"has_move:{value}"
            model.public_announcement(prop)
            title = f"{pokemon}: After observing {value} ({len(model)} remaining)"
        elif obs_type == "item":
            prop = f"has_item:{value}"
            model.public_announcement(prop)
            title = f"{pokemon}: After revealing {value} ({len(model)} remaining)"
        
        save_path = f"{save_prefix}_{i}.png" if save_prefix else None
        visualize_model(model, pokemon, title, save_path)

#demo
if __name__ == "__main__":
    from pokemon_data import get_sets
    model = KripkeModel()
    garchomp_sets = get_sets("Garchomp")
    model.add_worlds_from_pokemon_data("Garchomp", garchomp_sets)
    
    print("=== Initial State ===")
    visualize_model(model, "Garchomp", save_path="garchomp_initial.png")
    
    print("\n=== After Swords Dance ===")
    model.public_announcement("has_move:Swords Dance")
    visualize_model(model, "Garchomp", save_path="garchomp_after_sd.png")
    
    print("\n=== After Scale Shot ===")  
    model.public_announcement("has_move:Scale Shot")
    visualize_model(model, "Garchomp", save_path="garchomp_final.png")
