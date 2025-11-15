with staging as (
    select
        comic_id,
        title,
        safe_title,
        alt_text,
        img_url,
        transcript,
        link,
        publish_date
    from {{ ref('stg_xkcd_comics') }}
),

final as (
    select
        comic_id,
        title,
        safe_title,
        alt_text,
        img_url,
        transcript,
        link,
        publish_date,
        length(title) as title_length
    from staging
)

select *
from final

