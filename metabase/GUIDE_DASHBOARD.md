# Guide Metabase — Création du dashboard RetailPulse

> À suivre à la prochaine session. Le pipeline est fonctionnel : les 4 tables
> `mart.*` sont peuplées et prêtes à être visualisées.

## Étape 0 — Vérifier que la stack tourne

```bash
docker-compose up -d
docker-compose ps      # tous les services doivent être "Up" / "healthy"
```

Si besoin de re-générer les données : déclencher le DAG `retailpulse_dag`
depuis http://localhost:8080 (admin / admin).

---

## Étape 1 — Connexion à la base (premier lancement)

1. Ouvrir **http://localhost:3000**
2. Créer le compte admin (nom, email, mot de passe — à noter)
3. Au choix « Add your data » → **PostgreSQL** :

   | Champ          | Valeur                  |
   |----------------|-------------------------|
   | Display name   | RetailPulse             |
   | Host           | `postgres-retailpulse`  |
   | Port           | `5432`                  |
   | Database name  | `retailpulse`           |
   | Username       | `retailpulse`           |
   | Password       | `retailpulse`           |

4. **Save** → Metabase synchronise le schéma (voir les tables `mart.*`)

> ⚠️ Host = `postgres-retailpulse` (nom du service Docker), PAS `localhost` :
> Metabase tourne dans le même réseau Docker.

---

## Étape 2 — Les 4 visualisations à créer

Pour chacune : **+ New → Question → Raw data → RetailPulse → table** (ou éditeur SQL).

### 1. Évolution du chiffre d'affaires (Line chart)
- Table : `mart_daily_revenue`
- Axe X : `order_date` · Axe Y : `total_revenue`
- Type : **Line**
- Titre : « CA quotidien »

### 2. Commandes par état brésilien (Map ou Bar)
- Table : `mart_orders_by_state`
- Dimension : `customer_state` · Mesure : `total_orders`
- Type : **Bar** (trié décroissant) ou **Region map** (Brazil)
- Titre : « Volume de commandes par état »

### 3. Performance de livraison (Line)
- Table : `mart_delivery_perf`
- Axe X : `order_date` · Axe Y : `avg_delivery_days`
- Type : **Line**
- Titre : « Délai de livraison moyen (jours) »

### 4. Distribution des notes clients (Bar / Pie)
- Table : `mart_review_scores`
- Dimension : `review_score` · Mesure : `review_count`
- Type : **Bar** (ou Pie pour le %)
- Titre : « Répartition des notes (1-5) »

---

## Étape 3 — Assembler le dashboard

1. **+ New → Dashboard** → nom « RetailPulse — Vue d'ensemble »
2. **Add a card** → ajouter les 4 questions sauvegardées
3. Réorganiser/redimensionner les tuiles (2×2 conseillé)
4. **Save**

---

## Étape 4 — Pour le portfolio

- **Screenshot** du dashboard final → l'ajouter au `README.md`
  (section « Aperçu » avec `![dashboard](docs/dashboard.png)`)
- Optionnel : exporter le dashboard ou documenter les questions SQL
- Commit : `docs: ajout du dashboard Metabase et capture d'écran`

---

## Requêtes SQL de secours (si l'éditeur visuel coince)

```sql
-- CA quotidien
SELECT order_date, total_revenue FROM mart.mart_daily_revenue ORDER BY order_date;

-- Top 10 états
SELECT customer_state, total_orders FROM mart.mart_orders_by_state
ORDER BY total_orders DESC LIMIT 10;

-- Délai de livraison
SELECT order_date, avg_delivery_days FROM mart.mart_delivery_perf ORDER BY order_date;

-- Notes clients
SELECT review_score, review_count, pct_of_total FROM mart.mart_review_scores
ORDER BY review_score;
```
