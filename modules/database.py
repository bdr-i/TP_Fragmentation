import psycopg2
import pandas as pd

def get_connection():
    conn = psycopg2.connect(
        dbname="tp_db",
        user="tp_user",
        password="tp_password",
        host="localhost",
        port=5432
    )
    return conn

def execute_query(query):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(query)

        # Si SELECT → récupérer les résultats
        if query.strip().lower().startswith("select"):
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=colnames)
            cur.close()
            conn.close()
            return df

        conn.commit()
        cur.close()
        conn.close()
        return "OK"

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return f"Erreur SQL : {e}"
