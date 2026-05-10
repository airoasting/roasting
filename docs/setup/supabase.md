# Supabase Telemetry Backend Setup

## One-time setup (manual)

1. Create Supabase project at https://supabase.com (free tier).
2. Get project URL + anon key from Project Settings → API.
3. Run migration: copy `db/migrations/0001_init_telemetry.sql` into the SQL Editor and execute.
4. Add to repo secrets (GitHub Actions):
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
5. (Optional) Add to plugin manifest as bundled resource — for v0.1 we hardcode the URL into `scripts/telemetry.py` (anon key is safe to ship since RLS only allows INSERT).

## Free tier capacity

- 500 MB database, 2 GB egress/month.
- Estimated row size: ~250 bytes.
- Capacity: ~2M rows. v0.1 beta target: 50 users × 5 calls/day × 30 days = 7,500 rows ≪ 2M.

## Privacy invariants

The schema **explicitly** has no content columns:
- ❌ no xxxxx
- ❌ no BLACK output
- ❌ no RGSB comments
- ✅ case_id, score, rounds, anti-pattern counts, timestamp

Any future column addition must preserve this invariant.
