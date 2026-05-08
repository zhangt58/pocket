# Michigan Events Monitor

Interactive map and data for 7 Michigan event regions.

## Files
- `events_map_YYYY-MM-DD.html` — Interactive Leaflet map (open in browser)
- `events_final.json` — Raw event data

## Regions
| Region | Events | Source |
|--------|--------|--------|
| Detroit Metro | 44 | littleguidedetroit.com |
| Mt. Pleasant | 47 | meetmtp.com |
| Grand Rapids | 15 | experiencegr.com |
| Traverse City | 15 | traversecity.com |
| South Haven | 10 | southhavenmi.com |
| Battle Creek | 11 | battlecreekvisitors.org |
| Grand Haven | 8 | visitgrandhaven.com |

## Cron Job
Weekend events are scraped every Friday at 10am and posted to Discord.
Job ID: `6826679aaa01`

## Notes
- **Grand Rapids** — Added May 2026 via experiencegr.com (WordPress, 15 dated events)
- **Jackson** (experiencejackson.com) — Unscrapable: ITI Digital iframe calendar
- **Midland, MI** — No working visitor bureau event calendar found
- **Ann Arbor** (thingstodoinannarbor.com) — Unscrapable: blog-style vague dates
