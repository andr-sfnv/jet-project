-- Test: Cost must equal title_length * 5.0

select
    fct.comic_id,
    fct.cost_euros,
    dim.title_length,
    (dim.title_length * 5.0)::numeric(10, 2) as expected_cost
from {{ ref('fct_comic_metrics') }} as fct
inner join {{ ref('dim_comic') }} as dim
    on fct.comic_id = dim.comic_id
where fct.cost_euros != (dim.title_length * 5.0)::numeric(10, 2)

