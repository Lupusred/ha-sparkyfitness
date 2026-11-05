# API research and sensor contract

Research date: 2026-11-05. Source: CodeWithCJ/SparkyFitness, main commit
`120dc997f79220544fc72591d01c251090dcff1b`, package version 1.11.0.
Latest GitHub release confirmed via the GitHub API: `v1.11.0`, published
2026-10-30, commit
`0d8525e88ea7b116a92cd3aa35f622f7682201e2`.
The identity and measurement routes inspected are unchanged between that release
and main. Main additionally fixes emission of adjusted macro goals when only
macros change; this integration displays the goals the server actually returns.

The requested online API reference at
https://codewithcj.github.io/SparkyFitness/developer/api-reference/ and
https://developers.home-assistant.io/ could not be downloaded in this environment
(HTTP 403 network policy). The official Home Assistant DataUpdateCoordinator documentation and HACS
integration requirements were subsequently retrieved successfully from their
GitHub source repositories (`home-assistant/developers.home-assistant`,
`docs/integration_fetching_data.md`; `hacs/documentation`,
`source/docs/publish/integration.md`). Decisions were checked against actual server
routes, repositories, mobile-client types, those references and installed Home
Assistant APIs. API stability
across older versions is not claimed.

## Authentication and users

`middleware/authMiddleware.ts` accepts `x-api-key`; `auth.ts` configures Better
Auth API keys. Read-only scope is enforced server-side. Default API-key limit in
the inspected source: 100 requests per 60 seconds, configurable by the server.
The client makes sequential requests, stops on 429 and honors numeric/date
Retry-After (60 seconds minimum, 24 hours maximum); normal polling retries later.
No busy retry loop. Authentication failures (401/403) trigger key renewal.

`GET /api/identity/user` returns `authenticatedUserId`, `activeUserId` and identity
metadata. Only matching, nonempty IDs are accepted. IDs are checked every poll.
The integration sends no family/user-switch headers or `userId` query parameters.
Each account has a separate session and coordinator. A hash of normalized server
URL and user ID scopes device/entity IDs. API-key rotation preserves those IDs;
changing account is rejected. Different URL aliases represent different servers.

## Implemented requests

The read paths below are relative to the supplied server URL and use GET.
For the separate opt-in write layer, see [WRITING.md](WRITING.md).

| Endpoint | Actual response / use |
|---|---|
| `/api/identity/user` | Identity object; required for setup and polling |
| `/api/daily-summary?date=YYYY-MM-DD` | `calorieBalance`, `goals`, `adjustedGoals`, `foodEntries`, `supplementTotals`, `exerciseSessions`, `waterIntake` |
| `/api/measurements/check-in/latest-on-or-before-date?date=…` | Object or null; latest non-null body values, same-day steps and BMR |
| `/api/measurements/custom-categories` | List with `id`, `name`, `display_name`, `measurement_type` (unit), `frequency`, `data_type` |
| `/api/measurements/custom-entries/YYYY-MM-DD` | Today's category entries, `category_id`, `value`, `entry_date`, `entry_timestamp` |
| `/api/measurements/custom-entries?category_id=…&limit=1&orderBy=entry_timestamp.desc` | Latest entry per frequency `All` category |
| `/api/sleep?startDate=…&endDate=…` | Sleep-entry array for the selected day |

Six requests per ordinary update, plus one per `All` category. Missing optional
endpoints (404) omit their sensor families. Other HTTP errors or invalid top-level
response shapes fail the update; previous states become unavailable. No fabricated
zero substitutes are used for missing/invalid numeric values. Empty valid food or
workout lists produce zero totals. A syntactically valid identity alone does not
establish support for all optional sensor families.

Source references under `SparkyFitnessServer/`:
`SparkyFitnessServer.ts` (route mounts), `routes/auth/userProfileRoutes.ts`,
`routes/dailySummaryRoutes.ts`, `services/dailySummaryService.ts`,
`services/calorieBalanceService.ts`, `models/foodEntry.ts`,
`routes/measurementRoutes.ts`, `models/measurementRepository.ts`,
`routes/sleepRoutes.ts`, `models/sleepRepository.ts`, and
`integrations/garminconnect/garminMeasurementMapping.ts`.
All can be browsed at the [pinned source](https://github.com/CodeWithCJ/SparkyFitness/tree/120dc997f79220544fc72591d01c251090dcff1b).

## Sensors and meaning

| Family | Sensors / units |
|---|---|
| Calories | Eaten, goal, remaining and expenditure from `calorieBalance`, kcal |
| Nutrition | Protein, carbohydrate, fat, fiber, sugar (g), sodium (mg), corresponding supplied goals |
| Hydration | Today's total water, mL |
| Body | Weight, muscle and bone mass (kg); height, neck, waist, hips (cm); body fat/water (%); resting heart rate (bpm) when present |
| Activity | Same-day steps; measured BMR (kcal); workout count and duration (min) |
| Sleep | Longest sleep record's duration, time asleep, deep/REM/light seconds, score, oxygen saturation (%), overnight HRV (ms), when supplied |
| Custom | One sensor per category ID, with server-provided name/unit; numeric or text |

Macros use the server's flat food snapshot fields:
`nutrient * quantity / serving_size`, summed across entries, plus supplement
contributions. Missing/invalid inputs make that nutrient unknown. Adjusted goals
take precedence. Negative remaining calories are preserved. The calorie-balance
expenditure is SparkyFitness's configured calculation, **not necessarily Garmin's
measured total expenditure**. Garmin active/total calories, stress, resting pulse,
BMI and other imported metrics appear through their actual custom categories;
none are fabricated from step counts. Preset workouts use `total_duration_minutes`;
individual workouts use `duration_minutes`. The special Active Calories entry is
excluded from workout count/duration.

Sensors are discovered when fields/categories first appear. A null field creates
an unknown state; absent fields are not invented. Disappearing fields/categories
make existing entities unavailable (registry entries remain to preserve IDs and
history). Category renames preserve unique IDs. New categories appear on the next
poll without restart. Numeric state class is `measurement` except energy/volume sensors, which have
no state class: their daily totals, targets and remaining budgets should not be
accumulated as lifetime consumption statistics. No `total_increasing` is used,
since daily totals can decrease after edits. Physical-unit device classes are
assigned only for recognized units. Unknown custom units remain literal units.

Body values carry forward per the server's per-field SQL lookup. That response's
`entry_date` is the latest overall check-in, not each field's measurement date;
therefore this integration does not attach it to individual carried body values.
`All` custom categories carry their latest value/date forward; Daily/Hourly
categories use today's latest sample, not an invented sum/average. Dates are in
the configured time zone (default HA); match it to SparkyFitness. A minute-boundary
check requests fresh data after midnight and invalidates yesterday's daily states.
Sleep selects the longest daily record to avoid doubling overlapping provider
records; naps and stages from multiple records are not combined.

## Limits and unsupported features

- No Garmin sync triggers, OAuth login or family impersonation.
- Writes are opt-in from 0.2.0; computed sensors are never written back.
- No raw Garmin time series, ECG, GPS routes, workout set details or sleep-stage
  timeline entities. Imported numeric categories can expose available summaries.
- No custom *nutrient* discovery yet; custom *measurement* discovery is supported.
- No derived body-fat/BMR formulas or invented totals for absent API fields.
- No automatic historical backfill into Home Assistant Recorder.
- Older API versions are feature-detected only at optional endpoint level, not
  comprehensively supported. All optional endpoints missing can yield no sensors.
- `All` category lookup asks for the latest record; a future-dated latest record
  is ignored rather than used or searched backward.
- Multiple imported sources in one category use the newest timestamp; users
  should resolve duplicate/provider unit inconsistencies in SparkyFitness.
- Actual user deployment version, network reachability and live payload
  compatibility still need the bounded live test described in UNRAID.md.

## Write contract added in 0.2.0

Verified in the same pinned source: POST `/api/measurements/check-in` updates
only provided whitelisted fields (`models/measurementRepository.ts`). POST
`/api/measurements/custom-entries` validates category ownership server-side;
Daily/Hourly upserts are source-scoped, All/Unlimited inserts. POST
`/api/measurements/health-data` receives a single `water` record with a source ID;
per-record `processed`, `errors`, `skipped` must confirm success even for HTTP 200.
POST `/api/sleep/manual_entry` takes start/end/duration. POST `/api/food-entries`
and `/api/exercise-entries` create diary entries using existing library IDs.
The generic health ingestion route is never exposed for arbitrary types: Workout
can perform source/range cleanup and Nutrition maps unknown providers to Health
Connect in this upstream version. We deliberately use the dedicated diary routes.
