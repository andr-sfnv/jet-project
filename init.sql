-- Initialize warehouse database and schemas

create schema if not exists raw;
create schema if not exists staging;
create schema if not exists marts;

-- Create raw table for XKCD comics
create table if not exists raw.xkcd_comics (
    comic_id integer primary key,
    raw_json jsonb not null,
    load_ts timestamp not null default current_timestamp,
    load_id uuid not null,
    is_current boolean not null default true
);

create index idx_xkcd_comics_load_ts on raw.xkcd_comics(load_ts);
create index idx_xkcd_comics_load_id on raw.xkcd_comics(load_id);
create index idx_xkcd_comics_is_current on raw.xkcd_comics(is_current);
