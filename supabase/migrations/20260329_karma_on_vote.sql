-- Adjust the event author's karma whenever a vote is cast, flipped, or removed.
--
-- Delta logic:
--   INSERT  vote=+1  →  author karma +1
--   INSERT  vote=-1  →  author karma -1
--   UPDATE  flip     →  author karma +(NEW.vote - OLD.vote)  (+2 or -2)
--   DELETE  vote=+1  →  author karma -1
--   DELETE  vote=-1  →  author karma +1
--
-- SECURITY DEFINER is required because the voter is not the profile owner and
-- RLS on public.profiles would otherwise block the UPDATE.

create or replace function public.update_author_karma()
returns trigger language plpgsql security definer as $$
declare
  v_author_id uuid;
  v_delta     integer;
begin
  select author_id into v_author_id
  from public.events
  where id = coalesce(NEW.event_id, OLD.event_id);

  -- Scraper events have no author — nothing to do
  if v_author_id is null then
    return coalesce(NEW, OLD);
  end if;

  if TG_OP = 'INSERT' then
    v_delta := NEW.vote;
  elsif TG_OP = 'UPDATE' then
    v_delta := NEW.vote - OLD.vote;
  else -- DELETE
    v_delta := -OLD.vote;
  end if;

  if v_delta <> 0 then
    update public.profiles set karma = karma + v_delta where id = v_author_id;
  end if;

  return coalesce(NEW, OLD);
end;
$$;

create trigger event_votes_update_karma
  after insert or update or delete on public.event_votes
  for each row execute function public.update_author_karma();
