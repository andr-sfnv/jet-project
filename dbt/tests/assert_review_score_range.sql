-- Test: Customer review score must be between 1.0 and 10.0 (inclusive)

select comic_id, customer_review_score
from {{ ref('fct_comic_metrics') }}
where customer_review_score < 1.0 or customer_review_score > 10.0

