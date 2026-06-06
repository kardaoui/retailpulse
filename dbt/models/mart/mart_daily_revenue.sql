with orders as (
    select * from {{ ref('stg_orders') }}
    where order_status = 'delivered'
),

payments as (
    select * from {{ source('raw', 'payments') }}
),

daily as (
    select
        o.order_purchase_timestamp::date        as order_date,
        count(distinct o.order_id)              as total_orders,
        sum(p.payment_value::numeric)           as total_revenue,
        avg(p.payment_value::numeric)           as avg_order_value
    from orders o
    inner join payments p on o.order_id = p.order_id
    group by 1
)

select * from daily
order by order_date
