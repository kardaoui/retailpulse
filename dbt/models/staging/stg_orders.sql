with source as (
    select * from {{ source('raw', 'orders') }}
),

transformed as (
    select
        order_id,
        customer_id,
        order_status,
        -- Les CSV chargent les dates vides comme '' : nullif évite l'échec du cast
        nullif(order_purchase_timestamp, '')::timestamp      as order_purchase_timestamp,
        nullif(order_approved_at, '')::timestamp             as order_approved_at,
        nullif(order_delivered_carrier_date, '')::timestamp  as order_delivered_carrier_date,
        nullif(order_delivered_customer_date, '')::timestamp as order_delivered_customer_date,
        nullif(order_estimated_delivery_date, '')::timestamp as order_estimated_delivery_date
    from source
    where order_id is not null
      and customer_id is not null
)

select * from transformed
