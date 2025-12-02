
def rewrite_query(query, partitions):
    try:
        q = query.strip()
        q_upper = q.upper()

        # Vérification format
        if "SELECT" not in q_upper or "FROM" not in q_upper:
            return "Erreur : Format requis : SELECT ... FROM TP_Table"

        select_part = q_upper.split("SELECT")[1].split("FROM")[0].strip()

        # Gestion COUNT(*)
        is_count = select_part.startswith("COUNT(")

        if is_count:
            cols = ["count"]
        else:
            if select_part == "*":
                cols = ["*"]
            else:
                cols = [c.strip().lower() for c in select_part.split(",")]
        # GESTION WHERE 
        where_clause = ""
        if "WHERE" in q_upper:
            where_clause = q[ q_upper.index("WHERE") : ].strip()
        else:
            where_clause = ""

        # Valider FROM TP_Table
        from_part = q_upper.split("FROM")[1].split()[0].strip()
        #rendre minuscule pour comparaison avec les fragments
        from_part = from_part.lower()
        if from_part != "tp_table":
            return "Erreur : La requête doit être sur TP_Table"

        # Identifier les fragments nécessaires
        fragment_utilise = set()

        if cols == ["*"] or is_count:
            # toutes les colonnes peuvent être utilisées dans WHERE
            fragment_utilise = {i for i in range(len(partitions))}
        else:
            for col in cols:
                found = False
                for i, part in enumerate(partitions):
                    if col in [x.lower() for x in part]:
                        fragment_utilise.add(i)
                        found = True
                        break
                if not found:
                    return f"Erreur : La colonne {col} n'existe dans aucun fragment"

        # Ajouter colonnes utilisées dans WHERE
        if where_clause:
            for i, part in enumerate(partitions):
                for c in part:
                    if c.lower() in where_clause.lower():
                        fragment_utilise.add(i)

        fragment_utilise = sorted(fragment_utilise)

        # Construction de la clause SELECT

        if is_count:
            select_clause = "COUNT(*)"
        elif cols == ["*"]:
            # rassembler toutes les colonnes
            select_cols = []
            for part in partitions:
                for c in part:
                    if c not in select_cols:
                        select_cols.append(c)
            select_clause = ", ".join(select_cols)
        else:
            select_clause = ", ".join(cols)

        # Join et FROM
        sql = f"SELECT {select_clause} FROM Fragment_{fragment_utilise[0] + 1}"

        for idx in fragment_utilise[1:]:
            sql += f" JOIN Fragment_{idx + 1} USING(id)"

        # Ajouter la clause WHERE si utile
        if where_clause:
            sql += " " + where_clause

        return sql + ";"

    except Exception as e:
        return f"Erreur lors de la réécriture : {str(e)}"
