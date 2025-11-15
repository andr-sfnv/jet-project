-- Test: Views must be between 0 and 10000 (inclusive)

select comic_id, views
from {{ ref('fct_comic_metrics') }}
where views < 0 or views > 10000

