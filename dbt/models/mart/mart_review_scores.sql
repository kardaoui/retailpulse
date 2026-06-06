with reviews as (
    select * from {{ source('raw', 'reviews') }}
    where review_score is not null
      and review_score::int between 1 and 5
),

aggregated as (
    select
        review_score::int                                                        as review_score,
        count(*)                                                                 as review_count,
        round(100.0 * count(*) / sum(count(*)) over (), 2)                      as pct_of_total
    from reviews
    group by 1
)

select * from aggregated
order by review_score
