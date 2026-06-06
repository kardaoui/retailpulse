# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Présentation du projet

Pipeline de données e-commerce automatisé construit à des fins de portfolio.
Il ingère les données Olist (100k commandes brésiliennes), les transforme via dbt,
contrôle leur qualité avec Great Expectations, orchestre le tout avec Airflow,
et expose les KPIs dans un dashboard Metabase.

**Objectif** : démontrer un pipeline data complet (ingestion → transformation →
qualité → orchestration → visualisation) tel qu'attendu pour un poste MLOps / Data Engineer junior.

---

## Stack technique

| Couche         | Outil                   | Version cible |
|----------------|-------------------------|---------------|
| Orchestration  | Apache Airflow          | 2.8+          |
| Transformation | dbt-core + dbt-postgres | 1.7+          |
| Base de données| PostgreSQL              | 15            |
| Qualité data   | Great Expectations      | 0.18+         |
| Dashboard      | Metabase                | latest        |
| Broker         | Redis                   | 7             |
| Conteneurs     | Docker + Compose        | latest        |
| Langage        | Python                  | 3.11          |

---

## Architecture du projet

```
retailpulse/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── .env.example
│
├── data/
│   └── raw/                    # CSV Olist téléchargés ici (non versionnés)
│
├── ingestion/
│   ├── load_olist.py           # Script d'ingestion CSV → PostgreSQL
│   └── requirements.txt
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── raw/                # Couche 1 : données brutes copiées telles quelles
│   │   ├── staging/            # Couche 2 : nettoyage, typage, renommage
│   │   └── mart/               # Couche 3 : agrégats métiers (KPIs)
│   └── tests/
│
├── airflow/
│   ├── dags/
│   │   └── retailpulse_dag.py  # DAG principal
│   └── plugins/
│
├── great_expectations/
│   ├── expectations/           # Règles de qualité des données
│   └── checkpoints/
│
└── metabase/
    └── setup_notes.md          # Instructions de connexion dashboard
```

---

## Commandes essentielles

### Démarrer l'environnement complet
```bash
docker-compose up -d
```

### Arrêter l'environnement
```bash
docker-compose down
```

### Lancer l'ingestion des données
```bash
docker-compose exec airflow-webserver python /opt/airflow/ingestion/load_olist.py
```

### Lancer les transformations dbt
```bash
docker-compose exec airflow-webserver dbt run --project-dir /opt/dbt
```

### Lancer les tests dbt
```bash
docker-compose exec airflow-webserver dbt test --project-dir /opt/dbt
```

### Lancer les checks Great Expectations
```bash
docker-compose exec airflow-webserver great_expectations checkpoint run olist_checkpoint
```

### Accéder aux interfaces
- Airflow    → http://localhost:8080  (admin / admin)
- Metabase   → http://localhost:3000
- PostgreSQL → localhost:5432 (retailpulse / retailpulse)

---

## Modèle de données

### Dataset source : Olist (Kaggle)
9 fichiers CSV interconnectés, ~100k commandes (2016-2018)

### Schéma PostgreSQL cible

**raw** (copie exacte des CSV)
- raw.orders, raw.customers, raw.products
- raw.sellers, raw.order_items, raw.payments
- raw.reviews, raw.geolocation

**staging** (nettoyé, typé)
- stg_orders       : dates converties, statuts normalisés
- stg_customers    : villes nettoyées, état en majuscules
- stg_order_items  : prix et quantités validés

**mart** (KPIs métiers)
- mart_daily_revenue   : CA par jour
- mart_orders_by_state : commandes par état brésilien
- mart_delivery_perf   : délais de livraison moyens
- mart_review_scores   : notes clients agrégées

---

## Règles de qualité (Great Expectations)

Les expectations suivantes sont obligatoires avant tout run dbt :

- `order_id` : not null, unique
- `customer_id` : not null
- `order_purchase_timestamp` : not null, format datetime valide
- `payment_value` : >= 0
- `review_score` : between 1 and 5
- `order_status` : in `['delivered', 'shipped', 'canceled', 'invoiced', 'processing', 'unavailable', 'created', 'approved']`

---

## DAG Airflow : retailpulse_dag

**Schedule** : @daily (déclenché chaque nuit à minuit)

**Ordre des tâches** :
```
ingest_olist_csv
      ↓
run_great_expectations
      ↓
dbt_run_staging
      ↓
dbt_run_mart
      ↓
dbt_test
      ↓
notify_success
```

**Règles** :
- Si `run_great_expectations` échoue → pipeline bloqué, pas de dbt
- Retries : 2 tentatives, délai 5 minutes
- Timeout par tâche : 30 minutes

---

## Conventions de code

### Python
- Style : PEP8 strict, lint avec `ruff`
- Docstrings sur toutes les fonctions
- Variables d'environnement via `.env` (jamais de credentials en dur)
- Logging avec le module `logging` standard (pas de print)

### dbt
- Nommage des modèles : `raw_*`, `stg_*`, `mart_*`
- Tout modèle doit avoir : description, au moins 1 test `not_null`
- Les marts doivent avoir des tests `unique` sur leur clé primaire

### Git
- Branches : `feature/nom-feature`, `fix/nom-bug`
- Commits en français ou anglais, convention : `feat:`, `fix:`, `docs:`
- Ne jamais commiter le dossier `data/raw/` (dans .gitignore)

---

## Variables d'environnement (.env)

```env
POSTGRES_USER=retailpulse
POSTGRES_PASSWORD=retailpulse
POSTGRES_DB=retailpulse
POSTGRES_PORT=5432

AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0

METABASE_PORT=3000
```

---

## Ce que ce projet doit démontrer (pour les recruteurs)

1. Capacité à construire un pipeline data de bout en bout
2. Maîtrise de l'orchestration (Airflow DAGs)
3. Connaissance de dbt et du pattern raw/staging/mart
4. Approche data quality (Great Expectations)
5. Utilisation de Docker pour la reproductibilité
6. Code propre, documenté, versionné sur GitHub
