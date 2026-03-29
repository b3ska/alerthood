-- Fix events_with_coords: remove comment_count (column was dropped in 20260328_drop_comment_count)
create or replace function public.events_with_coords(
  max_rows int default 200
)
returns table (
  id uuid,
  area_id uuid,
  title text,
  description text,
  threat_type public.threat_type,
  severity public.severity_level,
  status public.event_status,
  occurred_at timestamptz,
  lat double precision,
  lng double precision,
  location_label text,
  source_type text,
  source_url text,
  relevance_score int,
  created_at timestamptz
) language sql stable security definer as $$
  select
    e.id, e.area_id, e.title, e.description,
    e.threat_type, e.severity, e.status, e.occurred_at,
    extensions.st_y(e.location) as lat,
    extensions.st_x(e.location) as lng,
    e.location_label, e.source_type, e.source_url,
    e.relevance_score, e.created_at
  from public.events e
  where e.status = 'active'
  order by e.occurred_at desc
  limit max_rows;
$$;

grant execute on function public.events_with_coords(int) to anon, authenticated;
