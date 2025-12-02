from modules.database import execute_query

def get_fragment_size(fragment_name):
    """
    fragment_name can be 'Fragment_1' or integer 1
    """
    if isinstance(fragment_name, int):
        fragment_name = f"Fragment_{fragment_name}"
    sql = f"SELECT pg_total_relation_size('{fragment_name}');"
    try:
        res = execute_query(sql)
        try:
            val = int(res.iloc[0, 0])
            return val
        except Exception:
            return 0
    except Exception:
        return 0

def compute_transport_cost(fragments_used, site_source, fragments_on_sites, latence_matrix):
    total_cost = 0
    for frag in fragments_used:
        # accept both int (1) or "Fragment_1"
        if isinstance(frag, int):
            frag_name = f"Fragment_{frag}"
        else:
            frag_name = frag

        frag_site = fragments_on_sites.get(frag_name)
        if frag_site is None:
            # try mapping by index if fragments_on_sites stores integers
            # fragments_on_sites is expected as {"Fragment_1":"Site_1", ...} or {"Fragment_1": "Site_2"}
            # fallback: if fragments_on_sites maps site->list, invert it
            try:
                inv = {}
                for s, lst in fragments_on_sites.items():
                    for idx in lst:
                        inv[f"Fragment_{idx}"] = s
                frag_site = inv.get(frag_name)
            except Exception:
                frag_site = None

        if frag_site is None:
            continue

        # get latency between site_source and frag_site
        try:
            latency = float(latence_matrix[site_source][frag_site])
        except Exception:
            latency = 0.0

        size = get_fragment_size(frag_name)  # bytes
        # simple model: cost = latency (ms) * size (bytes)
        total_cost += latency * size

    return total_cost

def simulate_execution_time(fragments_used, fragments_on_sites, latence_matrix, site_source="Site_1"):
    # fragments_used: list of ints or ["Fragment_1",...]
    # fragments_on_sites: either {"Fragment_1":"Site_2",...} OR {"Site_1":[1,3], ...}
    # latence_matrix: matrix from compute_latency_matrix

    # normalize fragments_on_sites to map fragment_name -> site
    mapping = {}
    # if fragments_on_sites maps site->list
    any_vals = next(iter(fragments_on_sites.values()))
    if isinstance(any_vals, list):
        for s, lst in fragments_on_sites.items():
            for idx in lst:
                mapping[f"Fragment_{idx}"] = s
    else:
        # assume fragment_name -> site
        mapping = fragments_on_sites

    # compute transport cost
    cost = compute_transport_cost(fragments_used, site_source, mapping, latence_matrix)
    # convert to ms (scale)
    T_transport = cost / 10000.0

    T_local = 20.0
    T_join = max(0, len(fragments_used) - 1) * 5.0
    T_total = T_local + T_transport + T_join

    return {
        "Fragments_used": fragments_used,
        "T_local_ms": round(T_local,3),
        "T_transport_ms": round(T_transport,3),
        "T_join_ms": round(T_join,3),
        "T_total_ms": round(T_total,3)
    }
