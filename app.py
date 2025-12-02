import streamlit as st
import pandas as pd
import graphviz

from modules.graphviz import draw_sites, assign_fragments_to_sites, generate_site_coordinates, compute_latency_matrix
from modules.database import execute_query
from modules.generate_data import generate_table_sql, generate_workload
from modules.parser import build_usage_matrix
from modules.partionner import run_kmeans
from modules.rewriter import rewrite_query
from modules.time_estimator import simulate_execution_time

# Configuration de la page
st.set_page_config(page_title="Fragmentation Verticale", layout="wide")
st.title("🔍 Outil Simple de Fragmentation Verticale")


# -------------------------- 1. Génération de données --------------------------
st.header("1. Génération des données")

n = st.number_input("Nombre de colonnes", min_value=30, value=30, step=10)
m = st.number_input("Nombre de lignes", min_value=10000, value=10000, step=10000)

if st.button("Générer"):
    with st.spinner("Génération en cours..."):
        create_stmt, insert_stmts = generate_table_sql(n, m)
        drop_result = execute_query("DROP TABLE IF EXISTS TP_Table;")
        st.write(f"Suppression ancienne table: {drop_result}")
        result_create = execute_query(create_stmt)
        st.write(f"Création table: {result_create}")

        batch_size = 100
        for i in range(0, len(insert_stmts), batch_size):
            batch = insert_stmts[i:i+batch_size]
            sql = "\n".join(batch)
            execute_query(sql)

        st.session_state.table_sql = create_stmt
        st.session_state.workload = generate_workload(n)
        st.session_state.attributes = [f"col{i}" for i in range(1, n + 1)]
        st.session_state.n_rows = m

    st.success(f"Table créée avec {m} lignes et {n} colonnes !")


# SQL créé
st.subheader("SQL généré")
if "table_sql" in st.session_state:
    st.code(st.session_state.table_sql)


# Workload
st.subheader("Workload SQL")
if "workload" in st.session_state:
    for q in st.session_state.workload:
        st.code(q)


# -------------------------- 2. Matrice d'usage --------------------------
st.header("2. Matrice d'usage")

if "workload" in st.session_state:
    matrix = build_usage_matrix(st.session_state.workload, st.session_state.attributes)
    st.session_state.matrix = matrix

    st.write("Matrice (requête × colonnes)")
    st.dataframe(matrix)


# -------------------------- 3. Partitionnement --------------------------
st.header("3. Partitionnement K-Means")

k = st.number_input("Nombre de fragments", min_value=2, value=2)

if st.button("Lancer K-Means"):
    if "matrix" in st.session_state:
        partitions = run_kmeans(st.session_state.matrix, st.session_state.attributes, k)
        st.session_state.partitions = partitions

        st.write(f"**{k} fragments créés :**")
        for i, part in enumerate(partitions):
            st.write(f"Fragment {i + 1}: {part}")
    else:
        st.warning("Veuillez d'abord générer la matrice d’usage.")


# Création des fragments SQL
if st.button("Créer les fragments dans la base"):
    if "partitions" not in st.session_state:
        st.warning("Lance d'abord K-Means.")
    else:
        for i, part in enumerate(st.session_state.partitions):
            cols_sql = ", ".join([f"{c} TEXT" for c in part if c != "id"])
            sql = f"""
            CREATE TABLE IF NOT EXISTS Fragment_{i+1} (
                id INT PRIMARY KEY,
                {cols_sql}
            );
            """
            st.code(sql)
            st.write(execute_query(sql))

        st.success("Fragments créés dans PostgreSQL 🎉")


# -------------------------- Distribution des sites --------------------------
nb_sites = st.number_input("Nombre de sites", min_value=2, value=2, max_value=max(2, k))

# Génération déclarative de la topologie (coords + latence)
if "coords" not in st.session_state or st.session_state.get("coords_sites") != nb_sites:
    coords = generate_site_coordinates(nb_sites)
    lat = compute_latency_matrix(coords)

    st.session_state.coords = coords
    st.session_state.latence = lat
    st.session_state.coords_sites = nb_sites

st.subheader("📍 Coordonnées des sites")
st.json(st.session_state.coords)

st.subheader("⏱️ Latence (calculée via distance)")
st.json(st.session_state.latence)

# Assign fragments to sites
if st.button("Assigner fragments aux sites"):
    if "partitions" not in st.session_state:
        st.warning("Lance d'abord K-Means.")
    else:
        sites = assign_fragments_to_sites(st.session_state.partitions, nb_sites)
        st.session_state.sites = sites
        st.write("Fragments assignés aux sites :")
        st.json(sites)

        # affichage du graphe (sans highlight initial)
        graph = draw_sites(sites, st.session_state.coords)
        st.graphviz_chart(graph)


# -------------------------- 4. Réécriture + Exécution --------------------------
st.header("4. Réécriture de requêtes + Exécution")

query = st.text_input("Écrire une requête SQL sur TP_Table :")

if st.button("Réécrire"):
    if "partitions" in st.session_state:
        rewrite = rewrite_query(query, st.session_state.partitions)
        st.code(rewrite)
        st.session_state.last_query = rewrite
    else:
        st.warning("Lance d'abord K-Means.")


# -------------------------- Execution, site selection, simulation ----------
if "last_query" in st.session_state:
    st.subheader("Exécution & simulation")

    # radiobox pour choisir le site d'exécution
    if "sites" in st.session_state:
        site_choice = st.radio("Choisir le site d'exécution:", list(st.session_state.sites.keys()))
    else:
        site_choice = st.radio("Choisir le site d'exécution:", ["Site_1"])

    # redraw graph with highlight
    if "sites" in st.session_state:
        graph = draw_sites(st.session_state.sites, st.session_state.coords, site_highlight=site_choice)
        st.graphviz_chart(graph)

    if st.button("Exécuter la requête réécrite"):
        st.write("🔎 Requête exécutée :")
        st.code(st.session_state.last_query)

        # Exécution réelle dans PostgreSQL
        result = execute_query(st.session_state.last_query)
        st.write("📌 Résultat :")
        st.write(result)

        # Détection des fragments utilisés (as indices)
        rewrite = st.session_state.last_query
        fragments_used = []
        for i in range(len(st.session_state.partitions)):
            if f"Fragment_{i+1}" in rewrite:
                fragments_used.append(i+1)

        st.write("🧩 Fragments impliqués :", fragments_used)

        # Simulation
        if "sites" in st.session_state and "latence" in st.session_state:
            res = simulate_execution_time(
                fragments_used,
                st.session_state.sites,
                st.session_state.latence,
                site_source=site_choice
            )
            st.subheader("Résultat de la simulation d'exécution")
            st.json(res)
        else:
            st.warning("Configure d'abord la distribution des sites.")
