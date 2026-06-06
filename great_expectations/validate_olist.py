"""Validation qualité des tables raw Olist via Great Expectations (API fluent 0.18).

Remplace l'approche CLI fichier (fragile en conteneur) par un contexte éphémère
créé à la volée. Sort en code 1 si une seule expectation échoue, ce qui bloque
le DAG Airflow en amont des transformations dbt.
"""

import logging
import os
import sys

from great_expectations.data_context import EphemeralDataContext
from great_expectations.data_context.types.base import (
    DataContextConfig,
    InMemoryStoreBackendDefaults,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ORDER_STATUSES = [
    "delivered", "shipped", "canceled", "invoiced",
    "processing", "unavailable", "created", "approved",
]


def get_connection_string() -> str:
    """Construit la chaîne de connexion PostgreSQL depuis l'environnement."""
    host = os.environ["POSTGRES_HOST"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def build_suites(context, datasource):
    """Définit les expectations par table et retourne la liste des validators."""
    validators = []

    # ── raw.orders ────────────────────────────────────────────────────────────
    orders = datasource.add_table_asset(name="orders", table_name="orders", schema_name="raw")
    v = context.get_validator(
        batch_request=orders.build_batch_request(),
        create_expectation_suite_with_name="olist_orders_suite",
    )
    v.expect_column_values_to_not_be_null("order_id")
    v.expect_column_values_to_be_unique("order_id")
    v.expect_column_values_to_not_be_null("customer_id")
    v.expect_column_values_to_not_be_null("order_purchase_timestamp")
    v.expect_column_values_to_be_in_set("order_status", ORDER_STATUSES)
    validators.append(("raw.orders", v))

    # ── raw.payments ──────────────────────────────────────────────────────────
    # Les colonnes raw sont en TEXT (copie exacte CSV) : on caste à la source
    # pour permettre les comparaisons numériques.
    payments = datasource.add_query_asset(
        name="payments",
        query="SELECT order_id, payment_value::numeric AS payment_value FROM raw.payments",
    )
    v = context.get_validator(
        batch_request=payments.build_batch_request(),
        create_expectation_suite_with_name="olist_payments_suite",
    )
    v.expect_column_values_to_not_be_null("order_id")
    v.expect_column_values_to_not_be_null("payment_value")
    v.expect_column_values_to_be_between("payment_value", min_value=0)
    validators.append(("raw.payments", v))

    # ── raw.reviews ───────────────────────────────────────────────────────────
    reviews = datasource.add_query_asset(
        name="reviews",
        query="SELECT order_id, review_score::numeric AS review_score FROM raw.reviews",
    )
    v = context.get_validator(
        batch_request=reviews.build_batch_request(),
        create_expectation_suite_with_name="olist_reviews_suite",
    )
    v.expect_column_values_to_not_be_null("order_id")
    v.expect_column_values_to_not_be_null("review_score")
    v.expect_column_values_to_be_between("review_score", min_value=1, max_value=5)
    validators.append(("raw.reviews", v))

    return validators


def main() -> None:
    """Exécute toutes les validations et bloque le pipeline en cas d'échec."""
    # Contexte strictement en mémoire : évite toute découverte/scaffolding de
    # projet sur le système de fichiers (problème de permissions en conteneur).
    context = EphemeralDataContext(
        project_config=DataContextConfig(
            store_backend_defaults=InMemoryStoreBackendDefaults()
        )
    )
    datasource = context.sources.add_postgres(
        name="retailpulse_postgres",
        connection_string=get_connection_string(),
    )

    all_passed = True
    for table_name, validator in build_suites(context, datasource):
        result = validator.validate()
        status = "OK" if result.success else "ÉCHEC"
        logger.info("Validation %s : %s", table_name, status)
        if not result.success:
            all_passed = False
            for r in result.results:
                if not r.success:
                    cfg = r.expectation_config
                    logger.error(
                        "  ✗ %s sur %s",
                        cfg.expectation_type,
                        cfg.kwargs.get("column", "?"),
                    )

    if not all_passed:
        logger.error("Validation qualité ÉCHOUÉE — pipeline bloqué.")
        sys.exit(1)

    logger.info("Toutes les validations qualité sont passées avec succès.")


if __name__ == "__main__":
    main()
