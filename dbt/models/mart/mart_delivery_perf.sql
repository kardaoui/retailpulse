with orders as (
    select * from {{ ref('stg_orders') }}
    where order_status = 'delivered'
      and order_delivered_customer_date is not null
      and order_purchase_timestamp is not null
),

perf as (
    select
        order_purchase_timestamp::date                                          as order_date,
        count(order_id)                                                         as delivered_orders,
        round(avg(
            extract(epoch from (order_delivered_customer_date - order_purchase_timestamp)) / 86400
        )::numeric, 2)                                                          as avg_delivery_days,
        -- Positif = livré avant l'estimation, négatif = livré en retard
        round(avg(
            extract(epoch from (order_estimated_delivery_date - order_delivered_customer_date)) / 86400
        )::numeric, 2)                                                          as avg_days_vs_estimate
    from orders
    group by 1
)

select * from perf
order by order_date
