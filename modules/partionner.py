from sklearn.cluster import KMeans
from modules.database import execute_query

# Fonction Kmeans
def run_kmeans(usage_matrix, attributes, k):

    # 1) KMEANS
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(usage_matrix.T)

    partitions = [[] for _ in range(k)]

    for attr, cluster_id in zip(attributes, labels):
        partitions[cluster_id].append(attr)

    # Trier les colonnes dans chaque fragment
    for p in partitions:
        p.sort()

    # Ajouter la clé primaire id
    for p in partitions:
        if "id" not in p:
            p.insert(0, "id")

    # Trier les fragments par taille (plus gros en premier)
    partitions.sort(key=lambda x: len(x), reverse=True)

    # 2) Récupérer le schéma de TP_Table
    schema = execute_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'tp_table'
        ORDER BY ordinal_position;
    """)

    if schema.empty:
        raise Exception("❌ ERREUR : TP_Table n'existe pas ou est vide. Génère les données avant K-Means.")

    # dictionnaire colonne → type SQL
    schema_dict = {
        row["column_name"].lower(): row["data_type"]
        for _, row in schema.iterrows()
    }

    # Suppression des anciens fragments
    drop_fragments()

    # Creation des fragments
    create_fragments(partitions, schema_dict)

    # Ajout des données dans les fragments
    data_fragments(partitions)

    return partitions

# Suppression des anciens fragments
def drop_fragments():
    for i in range(1, 50):
        execute_query(f"DROP TABLE IF EXISTS Fragment_{i} CASCADE;")


#Création des fragments
def create_fragments(partitions, schema_dict):

    for i, part in enumerate(partitions):
        fragment_name = f"Fragment_{i+1}"

        # Construction des colonnes SQL
        column_definitions = ""

        for col in part:
            col_lower = col.lower()

            if col_lower not in schema_dict:
                raise Exception(f"❌ Colonne inconnue dans TP_Table : {col}")

            # on récupère le vrai type issu de TP_Table
            col_type = schema_dict[col_lower].upper()

            # on ajoute dans la définition
            column_definitions += f"{col} {col_type}, "

        # nettoyer la fin " , "
        column_definitions = column_definitions.rstrip(", ")

        # Construction finale CREATE TABLE
        sql = (
            f"CREATE TABLE {fragment_name} ("
            f"{column_definitions}"
            f");"
        )

        execute_query(sql)

# Ajout des données dans les fragments
def data_fragments(partitions):

    for i, part in enumerate(partitions):
        fragment_name = f"Fragment_{i+1}"

        col_list = ", ".join(part)

        sql = (
            f"INSERT INTO {fragment_name} ({col_list}) "
            f"SELECT {col_list} FROM TP_Table;"
        )

        execute_query(sql)
