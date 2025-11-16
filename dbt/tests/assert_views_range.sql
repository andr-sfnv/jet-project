-- Test: Views must be between 0 and 10000 (inclusive)

select comic_id, view_count
from {{ ref('fct_comic_metrics') }}
where view_count < 0 or view_count > 10000

