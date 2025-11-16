with source as (
    select
        comic_id,
        raw_json,
        load_ts,
        load_id
    from {{ source('raw', 'xkcd_comics') }}
),

parsed as (
    select
        comic_id,
        load_ts,
        load_id,
        raw_json ->> 'title' as title,
        raw_json ->> 'safe_title' as safe_title,
        raw_json ->> 'alt' as alt_text,
        raw_json ->> 'img' as img_url,
        raw_json ->> 'transcript' as transcript,
        raw_json ->> 'year' as publish_year_str,
        raw_json ->> 'month' as publish_month_str,
        raw_json ->> 'day' as publish_day_str,
        raw_json ->> 'link' as link,
        raw_json ->> 'news' as news
    from source
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
        news,
        load_ts,
        load_id,
        make_date(
            publish_year_str::integer,
            publish_month_str::integer,
            publish_day_str::integer
        ) as publish_date
    from parsed
)

select *
from final
