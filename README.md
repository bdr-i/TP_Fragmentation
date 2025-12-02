# Outil de Fragmentation Verticale de Bases de Données

## Description
Application Streamlit pour l'analyse et la fragmentation verticale de tables PostgreSQL. Utilise K-Means pour partitionner les colonnes en fragments selon l'usage des requêtes.

## Installation

### 1. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Installer Graphviz (système)

**Sur MacOS:**
```bash
brew install graphviz
```

**Sur Linux (Ubuntu/Debian):**
```bash
sudo apt-get install graphviz
```

**Sur Windows:**
Télécharger depuis https://graphviz.org/download/

### 4. Configurer PostgreSQL (exemple)

```bash
# Créer la base de données et l'utilisateur
psql postgres

CREATE DATABASE tp_db;
CREATE USER tp_user WITH PASSWORD 'tp_password';
GRANT ALL PRIVILEGES ON DATABASE tp_db TO tp_user;
\q
```

## Lancement de l'application

```bash
streamlit run app.py
```

L'application s'ouvre sur http://localhost:8501

## Fonctionnalités

### 1. Génération de données
- Crée une table `Large_Dataset` avec colonnes INT, TEXT, DATE aléatoires
- Insère des lignes de données de test (batch insert)

### 2. Matrice d'usage
- Analyse les requêtes pour construire une matrice attribut-requête

### 3. Partitionnement K-Means
- Partitionne les colonnes en fragments basés sur la similarité d'usage

### 4. Réécriture de requêtes
- Réécrit les requêtes originales pour utiliser les fragments

## Initialiser le dépôt Git et publier sur GitHub

1. Initialiser le dépôt local et faire un commit initial:

```bash
cd "./"
git init -b main
git add .
git commit -m "Initial commit"
```

2. Si vous avez la CLI `gh` (GitHub CLI) configurée, créez et poussez le repo directement:

```bash
# crée le dépôt sous votre compte GitHub et pousse la branche main
gh repo create fragmentation-verticale --public --source=. --remote=origin --push
```

3. Sinon, créez un dépôt sur GitHub via l'interface web, puis ajoutez le remote et poussez:

```bash
git remote add origin git@github.com:<votre-compte>/fragmentation-verticale.git
git branch -M main
git push -u origin main
```

## Structure du projet

```
.
├── README.md
├── requirements.txt
├── app.py
├── modules/
│   ├── database.py       # Connexion PostgreSQL
│   ├── generate_data.py  # Génération de données
│   ├── parser.py         # Construction matrice d'usage
│   ├── partionner.py     # K-Means clustering
│   └── rewriter.py       # Réécriture de requêtes
└── venv/
```

## Dépendances

- **Streamlit**: Framework web interactif
- **Pandas**: Manipulation de données
- **Graphviz**: Visualisation de graphes
- **psycopg2-binary**: Connecteur PostgreSQL
- **scikit-learn**: Machine Learning (K-Means)
- **NumPy**: Calculs numériques

## Notes
- Le commit initial peut contenir des données générées; si vous préférez ne pas pousser les gros dumps, ajoutez `data/` ou `*.sql` au `.gitignore`.
- Adaptez le nom du dépôt `fragmentation-verticale` si vous préférez un autre nom.
