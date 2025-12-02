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
        words = ["Streamlit", "TP", "Projet", "Base", "Data", "Python", "SQL"]
        return "'" + random.choice(words) + "_" + str(random.randint(1, 999)) + "'"

    elif col_type == "DATE":
        base = datetime.date(2020, 1, 1)
        delta = datetime.timedelta(days=random.randint(0, 1600))
        d = base + delta
        return f"'{d.isoformat()}'"

    return "NULL"


# Création de TP_Table + insertions
def generate_table_sql(n_attributes, n_rows):
    col_types = {}
    for i in range(1, n_attributes + 1):
        col_types[f"col{i}"] = random_col_type()

    create_stmt = "CREATE TABLE TP_Table (\n id SERIAL PRIMARY KEY,\n"
    create_stmt += "".join([f" col{i} {col_types[f'col{i}']},\n"
                            for i in range(1, n_attributes + 1)])
    create_stmt = create_stmt.rstrip(",\n") + "\n);\n"

    insert_stmts = []
    for _ in range(n_rows):
        values = [random_value(col_types[f"col{i}"])
                  for i in range(1, n_attributes + 1)]
        insert_stmts.append(
            f"INSERT INTO TP_Table ({', '.join([f'col{i}' for i in range(1, n_attributes+1)])}) "
            f"VALUES ({', '.join(values)});"
        )

    return create_stmt, insert_stmts


# --- Chargement dynamique des types depuis la BD ---
from modules.database import execute_query

def get_column_types():
    sql = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'tp_table'
        ORDER BY ordinal_position;
    """
    df = execute_query(sql)
    types = {}
    for _, row in df.iterrows():
        types[row["column_name"]] = row["data_type"]
    return types


# Valeur cohérente pour WHERE selon type SQL réel
def workload_value(col_type):
    if col_type in ["integer", "int4"]:
        return str(random.randint(1, 500))

    if col_type in ["text", "varchar"]:
        return "'" + random.choice(["alpha", "test", "demo", "x", "hello"]) + "'"

    if col_type == "date":
        base = datetime.date(2020, 1, 1)
        d = base + datetime.timedelta(days=random.randint(0, 1600))
        return f"'{d.isoformat()}'"

    return "NULL"


# Workload généré aléatoirement
def generate_workload(n_attributes, n_queries=20):
    queries = []
    operators = ["=", "<", ">", "<=", ">=", "!="]
    agg_functions = ["COUNT", "SUM", "AVG", "MIN", "MAX"]

    col_types = get_column_types()

    for _ in range(n_queries):

        k = random.randint(1, min(8, n_attributes))
        selected = random.sample(range(1, n_attributes + 1), k)
        col_list = ", ".join([f"col{i}" for i in selected])

        query_type = random.choice([
            "simple", "where_simple", "where_complex",
            "aggregation", "order", "limit", "mixed"
        ])

        if query_type == "simple":
            sql = f"SELECT {col_list} FROM TP_Table;"

        elif query_type == "where_simple":
            col = f"col{random.randint(1, n_attributes)}"
            val = workload_value(col_types[col])
            op = random.choice(operators)
            sql = f"SELECT {col_list} FROM TP_Table WHERE {col} {op} {val};"

        elif query_type == "where_complex":
            colA = f"col{random.randint(1, n_attributes)}"
            colB = f"col{random.randint(1, n_attributes)}"
            valA = workload_value(col_types[colA])
            valB = workload_value(col_types[colB])
            opA = random.choice(operators)
            opB = random.choice(operators)
            joint = random.choice(["AND", "OR"])
            sql = (
                f"SELECT {col_list} FROM TP_Table "
                f"WHERE {colA} {opA} {valA} {joint} {colB} {opB} {valB};"
            )

        elif query_type == "aggregation":
            func = random.choice(agg_functions)
            col = f"col{random.randint(1, n_attributes)}"
            sql = f"SELECT {func}({col}) FROM TP_Table;"

        elif query_type == "order":
            order_col = f"col{random.randint(1, n_attributes)}"
            direction = random.choice(["ASC", "DESC"])
            sql = f"SELECT {col_list} FROM TP_Table ORDER BY {order_col} {direction};"

        elif query_type == "limit":
            limit_val = random.choice([10, 20, 50, 100])
            sql = f"SELECT {col_list} FROM TP_Table LIMIT {limit_val};"

        elif query_type == "mixed":
            colC = f"col{random.randint(1, n_attributes)}"
            valC = workload_value(col_types[colC])
            op = random.choice(operators)
            order_col = f"col{random.randint(1, n_attributes)}"
            direction = random.choice(["ASC", "DESC"])
            sql = (
                f"SELECT {col_list} FROM TP_Table "
                f"WHERE {colC} {op} {valC} "
                f"ORDER BY {order_col} {direction} LIMIT 50;"
            )

        else:
            sql = f"SELECT {col_list} FROM TP_Table;"

        queries.append(sql)

    return queries
