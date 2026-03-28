-- RPC: events with extracted lat/lng coordinates for frontend
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
  comment_count int,
  created_at timestamptz
) language sql stable as $$
  select
    e.id, e.area_id, e.title, e.description,
    e.threat_type, e.severity, e.status, e.occurred_at,
    extensions.st_y(e.location) as lat,
    extensions.st_x(e.location) as lng,
    e.location_label, e.source_type, e.source_url,
    e.relevance_score, e.comment_count, e.created_at
  from public.events e
  where e.status = 'active'
  order by e.occurred_at desc
  limit max_rows;
$$;

-- RPC: events in bounding box (used by safe route engine)
create or replace function public.events_in_bbox(
  min_lat double precision,
  max_lat double precision,
  min_lng double precision,
  max_lng double precision
)
returns table (
  id uuid,
  title text,
  threat_type public.threat_type,
  severity public.severity_level,
  occurred_at timestamptz,
  lat double precision,
  lng double precision,
  relevance_score integer
) language sql stable as $$
  select
    e.id, e.title, e.threat_type, e.severity, e.occurred_at,
    extensions.st_y(e.location) as lat,
    extensions.st_x(e.location) as lng,
    e.relevance_score
  from public.events e
  where e.status = 'active'
    and extensions.st_y(e.location) between min_lat and max_lat
    and extensions.st_x(e.location) between min_lng and max_lng
  order by e.occurred_at desc
  limit 500;
$$;

-- RPC: find nearest area to a point
create or replace function public.find_nearest_area(
  user_point extensions.geometry
)
returns table (
  id uuid,
  name text,
  city text,
  slug text,
  distance_km double precision
) language sql stable as $$
  select
    a.id, a.name, a.city, a.slug,
    extensions.st_distance(
      a.center::extensions.geography,
      user_point::extensions.geography
    ) / 1000.0 as distance_km
  from public.areas a
  where a.is_active = true
    and extensions.st_dwithin(
      a.center::extensions.geography,
      user_point::extensions.geography,
      a.radius_km * 1000
    )
  order by extensions.st_distance(a.center::extensions.geography, user_point::extensions.geography)
  limit 1;
$$;
