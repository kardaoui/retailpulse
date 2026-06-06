with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

aggregated as (
    select
        c.customer_state,
        count(distinct o.order_id)                                                as total_orders,
        count(distinct o.customer_id)                                             as unique_customers,
        round(
            100.0 * sum(case when o.order_status = 'delivered' then 1 else 0 end)
            / count(*), 2
        )                                                                         as delivery_rate_pct
    from orders o
    inner join customers c on o.customer_id = c.customer_id
    group by 1
)

select * from aggregated
order by total_orders desc
