with dim_comic as (
    select
        comic_id,
        title_length
    from {{ ref('dim_comic') }}
),

metrics as (
    select
        comic_id,
        -- Each letter costs 5 euros
        (title_length * 5.0)::numeric(10, 2) as cost_euros,
        -- Views are random number between 0 and 1 multiplied by 10000
        (random() * 10000)::integer as view_count,
        -- Reviews are a random number between 1.0 and 10.0
        (1.0 + random() * 9.0)::numeric(4, 1) as customer_review_score
    from dim_comic
),

final as (
    select
        comic_id,
        view_count,
        cost_euros,
        customer_review_score
    from metrics
)

select *
from final
