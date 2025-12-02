import random
import datetime

# Fontions pour générer des types de données aléatoires
def random_col_type():
    return random.choice(["INT", "TEXT", "DATE"])

# Fonction pour générer une valeur aléatoire selon le type  
def random_value(col_type):
    if col_type == "INT":
        return str(random.randint(1, 1000))

    elif col_type == "TEXT":
        words = ["Streamlit", "TP", "Projet", "BD", "Data", "Science", "Python", "SQL"]
        return "'" + random.choice(words) + "_" + str(random.randint(1, 999)) + "'"

    elif col_type == "DATE":
        base_date = datetime.date(2020, 1, 1)
        random_days = random.randint(0, 1500)
        v = base_date + datetime.timedelta(days=random_days)
        return f"'{v.isoformat()}'"


def generate_table_sql(n_attributes, n_rows):
    # 1. Colonnes + types
    col_types = {}
    for i in range(1, n_attributes + 1):
        col_types[f"col{i}"] = random_col_type()

    # 2. CREATE TABLE
    create_stmt = "CREATE TABLE Large_Dataset (\n id SERIAL PRIMARY KEY,\n "

    for col, t in col_types.items():
        create_stmt += f" {col} {t},\n"

    create_stmt = create_stmt.rstrip(",\n") + "\n);\n"

    # 3. INSERTS
    insert_stmts = []
    for _ in range(n_rows):
        values = [random_value(col_types[f"col{i}"]) for i in range(1, n_attributes + 1)]
        insert = (
            f"INSERT INTO Large_Dataset ({', '.join([f'col{i}' for i in range(1, n_attributes+1)])}) "
            f"VALUES ({', '.join(values)});"
        )
        insert_stmts.append(insert)

    return create_stmt, insert_stmts


def generate_workload(n_attributes, n_queries=20):
    queries = []
    for _ in range(n_queries):
        k = random.randint(1, 6)
        selected = random.sample(range(1, n_attributes+1), k)
        col_list = ", ".join([f"col{i}" for i in selected])
        queries.append(f"SELECT {col_list} FROM Large_Dataset WHERE id < 100;")
    return queries
