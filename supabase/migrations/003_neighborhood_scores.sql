-- Add safety scoring columns to areas
alter table public.areas
  add column if not exists crime_count int not null default 0,
  add column if not exists crime_rate_per_km2 numeric(8,2) not null default 0,
  add column if not exists poverty_index numeric(5,2) not null default 0,
  add column if not exists safety_score numeric(5,2) not null default 50,
  add column if not exists score_updated_at timestamptz;
