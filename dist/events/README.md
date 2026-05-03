# Michigan Events Monitor

Interactive map and data for 6 Michigan event regions.

## Files
- `hn_events_map_2026-05-03.html` — Interactive Leaflet map (open in browser)
- `events_final.json` — Raw event data (135 events)

## Regions
| Region | Events | Source |
|--------|--------|--------|
| Detroit Metro | 44 | littleguidedetroit.com |
| Mt. Pleasant | 47 | meetmtp.com |
| Traverse City | 15 | traversecity.com |
| South Haven | 10 | southhavenmi.com |
| Battle Creek | 11 | battlecreekvisitors.org |
| Grand Haven | 8 | visitgrandhaven.com |

## Cron Job
Weekend events are scraped every Friday at 10am and posted to Discord.
Job ID: `6826679aaa01`

## Notes
- **Jackson** (experiencejackson.com) — Unscrapable: ITI Digital iframe calendar
- **Ann Arbor** (thingstodoinannarbor.com) — Unscrapable: blog-style vague dates
