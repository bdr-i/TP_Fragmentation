import graphviz
import random
import math

def assign_fragments_to_sites(partitions, nb_sites):
    sites = {f"Site_{i+1}": [] for i in range(nb_sites)}
    for i, part in enumerate(partitions):
        site_id = (i % nb_sites) + 1
        sites[f"Site_{site_id}"].append(i+1)  # stocker l'indice du fragment (1-based)
    return sites

def generate_site_coordinates(nb_sites, seed=None):
    if seed is not None:
        random.seed(seed)
    coords = {}
    angle_step = 360 / nb_sites
    radius = 40
    for i in range(1, nb_sites+1):
        
        angle = math.radians(i * angle_step)
        x = int(50 + radius * math.cos(angle) + random.randint(-8,8))
        y = int(50 + radius * math.sin(angle) + random.randint(-8,8))
        coords[f"Site_{i}"] = (x, y)
    return coords

def compute_latency_matrix(coords, factor=1.2):
    lat = {}
    for si, (x1, y1) in coords.items():
        lat[si] = {}
        for sj, (x2, y2) in coords.items():
            if si == sj:
                lat[si][sj] = 0.0
            else:
                d = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                lat[si][sj] = round(d * factor, 3)  # en ms
    return lat


def draw_sites(sites, coords, site_highlight=None):
    
    dot = graphviz.Digraph("Sites", format="png")
    dot.attr(rankdir="LR")
    dot.attr('node', shape='box', style='rounded,filled')

    # Ajout des noeuds
    for site, frags in sites.items():
        x, y = coords.get(site, (0,0))
        label = f"{site}\\n({x},{y})\\n" + "\\n".join([f"Fragment_{f}" for f in frags])
        if site == site_highlight:
            dot.node(site, label, color="lightgreen", fillcolor="lightgreen")
        else:
            dot.node(site, label, color="lightblue", fillcolor="lightblue")

    # Ajout des arêtes avec latence
    for si, (x1, y1) in coords.items():
        for sj, (x2, y2) in coords.items():
            if si == sj:
                continue
            d = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            # Permettre d'éviter les doublons
            if si < sj:
                dot.edge(si, sj, label=f"{round(d,1)}", fontsize="8")
    return dot
