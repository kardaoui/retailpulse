"""Ingestion des fichiers CSV Olist vers PostgreSQL (schéma raw)."""

import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("DATA_DIR", "/opt/airflow/data/raw"))

CSV_TABLE_MAP = {
    "olist_orders_dataset.csv": "orders",
    "olist_customers_dataset.csv": "customers",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "product_category_translation",
}


def get_engine():
    """Crée le moteur SQLAlchemy à partir des variables d'environnement."""
    host = os.environ["POSTGRES_HOST"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    port = os.getenv("POSTGRES_PORT", "5432")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


def load_csv(engine, csv_path: Path, table_name: str) -> None:
    """Charge un CSV dans raw.<table_name>, en remplaçant les données existantes."""
    logger.info("Chargement de %s → raw.%s", csv_path.name, table_name)
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    df.to_sql(table_name, engine, schema="raw", if_exists="replace", index=False)
    logger.info("raw.%s : %d lignes chargées", table_name, len(df))


def main() -> None:
    """Point d'entrée principal : charge tous les CSV disponibles."""
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.commit()

    loaded, skipped = 0, 0
    for filename, table in CSV_TABLE_MAP.items():
        csv_path = DATA_DIR / filename
        if not csv_path.exists():
            logger.warning("Fichier introuvable, ignoré : %s", csv_path)
            skipped += 1
            continue
        load_csv(engine, csv_path, table)
        loaded += 1

    logger.info("Ingestion terminée — %d table(s) chargée(s), %d ignorée(s)", loaded, skipped)
    if loaded == 0:
        raise RuntimeError(f"Aucun fichier CSV trouvé dans {DATA_DIR}")


if __name__ == "__main__":
    main()
