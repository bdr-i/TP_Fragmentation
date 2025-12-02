import streamlit as st
import pandas as pd
import graphviz

from modules.graphviz import draw_sites, assign_fragments_to_sites
from modules.database import execute_query
from modules.generate_data import generate_table_sql, generate_workload
from modules.parser import build_usage_matrix
from modules.partionner import run_kmeans
from modules.rewriter import rewrite_query

st.set_page_config(page_title="Fragmentation Verticale", layout="wide")
st.title("🔍 Outil Simple de Fragmentation Verticale")

# -------------------------- Génération de données --------------------------

st.header("1.Génération des données")

n = st.number_input("Nombre de colonnes", min_value=30, value=30, step=10)
m = st.number_input("Nombre de lignes", min_value=10000, value=10000, step=10000)

if st.button("Générer"):
    with st.spinner("Génération en cours..."):
        # Générer le SQL
        create_stmt, insert_stmts = generate_table_sql(n, m)

        # Supprimer la table si elle existe
        drop_result = execute_query("DROP TABLE IF EXISTS TP_Table;")
        st.write(f"Suppression ancienne table: {drop_result}")

        # Créer la table
        result_create = execute_query(create_stmt)
        st.write(f"Création table: {result_create}")
        
        # Insérer les données (par batch pour éviter trop de requêtes)
        batch_size = 100
        for i in range(0, len(insert_stmts), batch_size):
            batch = insert_stmts[i:i+batch_size]
            batch_sql = "\n".join(batch)
            execute_query(batch_sql)
        
        # Sauvegarder dans session_state
        st.session_state.table_sql = create_stmt
        st.session_state.workload = generate_workload(n)
        st.session_state.attributes = [f"col{i}" for i in range(1, n+1)]
        st.session_state.n_rows = m

    st.success(f"✅ Table créée avec {m} lignes et {n} colonnes !")

st.subheader("SQL généré")
if "table_sql" in st.session_state:
    st.code(st.session_state.table_sql)
    if "n_rows" in st.session_state:
        st.info(f"+ {st.session_state.n_rows} lignes de données insérées")

st.subheader("Workload SQL")
if "workload" in st.session_state:
    for q in st.session_state.workload:
        st.code(q)

# -------------------------- La matrice d'usage --------------------------

st.header("2. Matrice d'usage")

if "workload" in st.session_state:
    matrix = build_usage_matrix(st.session_state.workload, st.session_state.attributes)
    st.session_state.matrix = matrix

    st.write("Matrice (requête × colonnes)")
    st.dataframe(matrix)

# --------------------------  Partionnement --------------------------

st.header("3 Partitionnement K-Means")

k = st.number_input("Nombre de fragments", min_value=2, value=2)

if st.button("Lancer K-Means"):
    if "matrix" in st.session_state:
        partitions = run_kmeans(st.session_state.matrix, st.session_state.attributes, k)
        st.session_state.partitions = partitions
        
        st.write(f"**{k} fragments créés :**")
        for i, part in enumerate(partitions):
            st.write(f"Fragment {i+1}: {part}")
    else:
        st.warning("Veuillez d'abord générer la matrice d'usage (étape 2)")

if st.button("Créer les fragments dans la base"):
    if "partitions" in st.session_state:
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

        st.success("Tables des fragments créées dans PostgreSQL 🎉")
    else:
        st.warning("Veuillez d'abord lancer K-Means pour créer les partitions")

nb_sites = st.number_input("Nombre de sites", min_value=2, value=2)

if st.button("Assigner fragments aux sites"):
    sites = assign_fragments_to_sites(st.session_state.partitions, nb_sites)
    st.session_state.sites = sites
    st.write("Fragments assignés aux sites :", sites)

    # Dessiner
    graph = draw_sites(sites, st.session_state.partitions)
    st.graphviz_chart(graph)

# -------------------------- Réécriture de requêtes --------------------------

st.header("4 Réécriture de requêtes + Exécution")

query = st.text_input("Écrire une requête SQL sur TP_Table :")

if st.button("Réécrire"):
    if "partitions" in st.session_state:
        if not query.strip():
            st.warning("Veuillez entrer une requête SQL")
        else:
            rewritten = rewrite_query(query, st.session_state.partitions)
            st.code(rewritten)
            st.session_state.last_query = rewritten
    else:
        st.warning("Veuillez d'abord créer les partitions avec K-Means")

# Ajouter un bouton pour exécuter la requête réécrite
if "last_query" in st.session_state:
    if st.button("Exécuter la requête réécrite"):
        result = execute_query(st.session_state.last_query)
        st.write(result)
