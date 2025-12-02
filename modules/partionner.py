from sklearn.cluster import KMeans
from modules.database import execute_query

def run_kmeans(usage_matrix, attributes, k):

    # 1 KMEANS
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(usage_matrix.T)

    partitions = [[] for _ in range(k)]

    for attr, cluster_id in zip(attributes, labels):
        partitions[cluster_id].append(attr)

    # Trie les colonnes
    for p in partitions:
        p.sort()

    # Ajoute la PK
    for p in partitions:
        p.insert(0, "id")

    # Trie les fragments par taille
    partitions.sort(key=lambda x: len(x), reverse=True)

    # 2 Supprimer les anciens fragments 
    drop_fragments()

    # 3 Créer les nouveaux fragments 
    create_fragments(partitions)

    # 4 Remplir automatiquement 
    data_fragments(partitions)

    return partitions


def drop_fragments():
    # Supprimer les fragments Fragment_i existants
    for i in range(1, 50):
        execute_query(f"DROP TABLE IF EXISTS Fragment_{i} CASCADE;")


def create_fragments(partitions):
    """Créer les tables Fragment_i avec les bons types."""
    
    for i, part in enumerate(partitions):
        fragment_name = f"Fragment_{i+1}"

        # Récupérer les types depuis TP_Table
        column_definitions = ""
        for col in part:
            if col != "id":
                result = execute_query(
                    f"""
                    SELECT data_type 
                    FROM information_schema.columns
                    WHERE table_name = 'TP_Table'
                    AND column_name = '{col}';
                    """
                )

                # récupérer le type depuis le DataFrame
                col_type = result.iloc[0, 0]
                column_definitions += f"{col} {col_type}, "

        column_definitions = column_definitions.rstrip(", ")

        sql = (
            f"CREATE TABLE {fragment_name} ("
            f"id INT PRIMARY KEY, "
            f"{column_definitions}"
            f");"
        )

        execute_query(sql)

def data_fragments(partitions):
    # Remplir les fragments avec les données de TP_Table

    for i, part in enumerate(partitions):
        fragment_name = f"Fragment_{i+1}"

        cols = [c for c in part]
        col_list = ", ".join(cols)

        sql = (
            f"INSERT INTO {fragment_name} ({col_list}) "
            f"SELECT {col_list} FROM TP_Table;"
        )

        execute_query(sql)
