-- Initialize warehouse database and schemas

create schema if not exists raw;

-- Create raw table for XKCD comics
create table if not exists raw.xkcd_comics (
    comic_id integer primary key,
    raw_json jsonb not null,
    load_ts timestamp not null default current_timestamp,
    load_id uuid not null
);

create index if not exists idx_xkcd_comics_load_ts on raw.xkcd_comics(load_ts);
create index if not exists idx_xkcd_comics_load_id on raw.xkcd_comics(load_id);
