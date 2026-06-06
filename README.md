# RetailPulse — Pipeline de données e-commerce

Pipeline de données end-to-end construit sur le dataset **Olist** (~100 000 commandes brésiliennes, 2016-2018).  
Projet portfolio démontrant les compétences attendues pour un poste **Data Engineer / MLOps junior**.

---

## Architecture

```
CSV Olist (data/raw/)
        │
        ▼
┌──────────────────┐
│  load_olist.py   │  Ingestion : pandas → PostgreSQL (schéma raw)
└──────────────────┘
        │
        ▼
┌──────────────────────┐
│  Great Expectations  │  Validation qualité (bloque le pipeline si KO)
└──────────────────────┘
        │
        ▼
┌──────────────────┐
│   dbt staging    │  Nettoyage, typage, renommage
└──────────────────┘
        │
        ▼
┌──────────────────┐
│    dbt mart      │  Agrégats métiers (KPIs)
└──────────────────┘
        │
        ▼
┌──────────────────┐
│    Metabase      │  Dashboard interactif
└──────────────────┘
```

Le tout est orchestré par **Apache Airflow** (DAG `@daily`) et entièrement conteneurisé avec **Docker Compose**.

---

## Stack technique

| Couche         | Outil                   | Version |
|----------------|-------------------------|---------|
| Orchestration  | Apache Airflow          | 2.8+    |
| Transformation | dbt-core + dbt-postgres | 1.7+    |
| Base de données| PostgreSQL              | 15      |
| Qualité data   | Great Expectations      | 0.18+   |
| Dashboard      | Metabase                | latest  |
| Broker         | Redis                   | 7       |
| Conteneurs     | Docker + Compose        | latest  |
| Langage        | Python                  | 3.11    |

---

## Modèle de données (3 couches dbt)

```
raw.*          ← Copie exacte des CSV (chargée par load_olist.py)
staging.*      ← Données nettoyées et typées
mart.*         ← KPIs métiers agrégés
```

### Tables marts exposées dans Metabase

| Modèle                  | Description                                      |
|-------------------------|--------------------------------------------------|
| `mart_daily_revenue`    | Chiffre d'affaires et nombre de commandes / jour |
| `mart_orders_by_state`  | Volume de commandes par état brésilien           |
| `mart_delivery_perf`    | Délai de livraison moyen vs estimation           |
| `mart_review_scores`    | Distribution des notes clients (1 à 5)          |

---

## DAG Airflow

```
ingest_olist_csv
      ↓
run_great_expectations   ← bloque si la qualité est insuffisante
      ↓
dbt_run_staging
      ↓
dbt_run_mart
      ↓
dbt_test
      ↓
notify_success
```

- **Schedule** : `@daily`  
- **Retries** : 2 tentatives, délai de 5 min  
- **Timeout** : 30 min par tâche

---

## Règles de qualité (Great Expectations)

| Champ                        | Règle                                    |
|------------------------------|------------------------------------------|
| `order_id`                   | not null, unique                         |
| `customer_id`                | not null                                 |
| `order_purchase_timestamp`   | not null, format datetime valide         |
| `payment_value`              | >= 0                                     |
| `review_score`               | entre 1 et 5                             |
| `order_status`               | valeurs autorisées uniquement            |

---

## Lancer le projet

### Pré-requis
- Docker & Docker Compose
- Dataset Olist dans `data/raw/` ([télécharger sur Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce))

### Démarrage

```bash
# 1. Cloner le repo
git clone https://github.com/kardaoui/retailpulse.git
cd retailpulse

# 2. Configurer l'environnement
cp .env.example .env

# 3. Construire et démarrer la stack
docker-compose up -d --build

# 4. Accéder aux interfaces
#    Airflow  → http://localhost:8080  (admin / admin)
#    Metabase → http://localhost:3000
```

### Lancer le pipeline manuellement

```bash
# Ingestion CSV → PostgreSQL
docker-compose exec airflow-webserver python /opt/airflow/ingestion/load_olist.py

# Validation qualité
docker-compose exec airflow-webserver great_expectations checkpoint run olist_checkpoint

# Transformations dbt
docker-compose exec airflow-webserver dbt run  --project-dir /opt/dbt
docker-compose exec airflow-webserver dbt test --project-dir /opt/dbt
```

---

## Structure du projet

```
retailpulse/
├── Dockerfile                   # Image Airflow custom (dbt + GE inclus)
├── docker-compose.yml           # Stack complète (7 services)
├── requirements-airflow.txt
├── scripts/
│   └── init_schemas.sql         # Crée les schémas raw/staging/mart au démarrage
├── ingestion/
│   └── load_olist.py            # CSV → raw.*
├── dbt/
│   ├── models/
│   │   ├── raw/                 # sources.yml (définitions Olist)
│   │   ├── staging/             # stg_orders, stg_customers, stg_order_items
│   │   └── mart/                # 4 modèles KPI
│   └── macros/
│       └── generate_schema_name.sql
├── airflow/
│   └── dags/
│       └── retailpulse_dag.py
├── great_expectations/
│   ├── expectations/            # 3 suites (orders, payments, reviews)
│   └── checkpoints/
│       └── olist_checkpoint.yml
└── metabase/
    └── setup_notes.md
```

---

## Ce que ce projet démontre

- **Ingestion** : chargement de données réelles (~100k lignes) via pandas et SQLAlchemy
- **Data quality** : gate obligatoire avec Great Expectations avant toute transformation
- **Transformation** : pattern raw → staging → mart avec dbt, tests intégrés
- **Orchestration** : DAG Airflow avec retries, timeout et gestion des dépendances
- **Reproductibilité** : stack 100% Docker, zéro installation manuelle
- **Bonnes pratiques** : PEP8, logging, variables d'environnement, .gitignore strict
