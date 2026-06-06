# Connexion Metabase → PostgreSQL RetailPulse

1. Ouvrir http://localhost:3000
2. Créer un compte administrateur au premier lancement
3. **Ajouter une base de données** → PostgreSQL :
   - Host : `postgres-retailpulse`
   - Port : `5432`
   - Database name : `retailpulse`
   - Username : `retailpulse`
   - Password : `retailpulse`
4. Cliquer sur **Save**

## Tableaux de bord suggérés

| Question                  | Modèle source          |
|---------------------------|------------------------|
| CA quotidien              | mart.mart_daily_revenue   |
| Commandes par état        | mart.mart_orders_by_state |
| Performance de livraison  | mart.mart_delivery_perf   |
| Distribution des notes    | mart.mart_review_scores   |
