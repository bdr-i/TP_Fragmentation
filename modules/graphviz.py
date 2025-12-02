import graphviz

def draw_sites(sites, partitions):
    dot = graphviz.Digraph("Sites", format="png")
    dot.attr(rankdir="LR")  # disposition horizontale

    # 1) Un nœud par site
    for site, frags in sites.items():
        label = f"{site}\n" + "\n".join([f"Fragment_{f}" for f in frags])
        dot.node(site, label, shape="box", style="rounded,filled", color="lightblue")
    return dot

def assign_fragments_to_sites(partitions, nb_sites):
    sites = {f"Site_{i+1}": [] for i in range(nb_sites)}

    for i, part in enumerate(partitions):
        site_id = (i % nb_sites) + 1
        sites[f"Site_{site_id}"].append(i+1)  # Fragment indices start at 1

    return sites