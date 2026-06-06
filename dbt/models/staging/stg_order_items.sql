with source as (
    select * from {{ source('raw', 'order_items') }}
),

transformed as (
    select
        order_id,
        nullif(order_item_id, '')::int            as order_item_id,
        product_id,
        seller_id,
        nullif(shipping_limit_date, '')::timestamp as shipping_limit_date,
        nullif(price, '')::numeric                as price,
        nullif(freight_value, '')::numeric        as freight_value
    from source
    where order_id is not null
      and nullif(price, '')::numeric >= 0
      and nullif(freight_value, '')::numeric >= 0
)

select * from transformed
