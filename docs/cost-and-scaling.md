# Cost and scaling analysis

Planning date: 24 October 2026. USD per month. The workbook contains **illustrative engineering budgets, not verified vendor quotations**. Public pricing pages were consulted, but exact regional capacity/egress/backup configurations have not been quoted. Taxes, support contracts, discounts, free-tier credits, and incident costs are excluded. Replace all budget inputs with approved quotes before purchasing.

## Workload assumptions

20% of registered users are active daily; each active user makes 20 dynamic requests/day. Average transferred response including amortized local static assets: 100 KB. Month: 30 days. Peak: 10 times average request rate. 1% of users publish two articles per month; article plus associated comments/metadata: 50 KB; database storage provisioned at 3x raw content for indexes/overhead, before backups. Existing content retention is indefinite. Static covers do not grow with article count.

| Registered users | Monthly requests | Transfer GB/month (decimal) | Peak requests/sec | DB growth GB/month |
|---:|---:|---:|---:|---:|
| 100 | 12,000 | 1.2 | 0.046 | 0.0003 |
| 1,000 | 120,000 | 12 | 0.463 | 0.003 |
| 10,000 | 1,200,000 | 120 | 4.63 | 0.03 |
| 1,000,000 | 120,000,000 | 12,000 | 463 | 3 |

Registered users alone do not establish capacity. Traffic bursts, content length, search load, bot traffic, concurrent editors, and cache hit rates dominate. These figures are scenario assumptions, not benchmark results.

## Option A: VPS + Supabase PostgreSQL

At 100/1,000 users: a modest Linux VPS, Gunicorn, reverse proxy/TLS and WhiteNoise; Supabase PostgreSQL over SSL. At 10,000: larger or two application nodes if availability requires it, database connection budgeting, query measurement, log/backup monitoring. At 1,000,000: multiple app nodes behind a load balancer, static CDN delivery, larger managed database/replicas where suitable, full-text search indexes, measured connection pooling, and tested failover. No Redis or microservices are needed for this MVP.

VPS benefits: simple operations and comparatively predictable base compute cost. Costs: manual OS patching, deploy orchestration, failover planning, and maintenance labor. Supabase pricing, backups/PITR and connection limits must be reviewed independently. Keep application and database regions close.

## Option B: AWS application hosting + Supabase PostgreSQL

At 100/1,000: Lightsail Linux or a small EC2 instance; retain mandated Supabase PostgreSQL. At 10,000: assess EC2 plus load balancer and a second node for availability. At 1,000,000: autoscaled EC2, ALB, static distribution, centralized logs/metrics, bounded egress and database connection limits. RDS is a possible future database alternative, but would depart from the intended Supabase provider and is not part of this implementation.

AWS benefits: managed networking/monitoring and a path to multiple availability zones. Costs: more IAM/network configuration, variable egress, log ingestion, load balancer charges, and possible cross-provider database transfer. Availability depends on both AWS and Supabase, not just EC2.

## Illustrative monthly budgets

The workbook itemizes compute, database, storage, backups, bandwidth, monitoring, domain, and maintenance at all four levels for each option. Maintenance uses a hypothetical $40/hour internal labor rate. Domain uses a $15/year placeholder. Values intentionally remain editable; they are not claims about current plan prices.

| Approach | 100 users | 1,000 users | 10,000 users | 1,000,000 users |
|---|---:|---:|---:|---:|
| VPS total including labor | $125.25 | $187.25 | $434.25 | $3,906.25 |
| AWS total including labor | $165.25 | $257.25 | $704.25 | $6,866.25 |

Totals are planning arithmetic only. Validate them against workload tests and vendor quotes. Budget hours increase with operational complexity; they are not staffing forecasts. Neither option is guaranteed to sustain the largest workload without load tests and database/search redesign as needed.

## Sources and quote checklist

- [DigitalOcean Droplet pricing](https://www.digitalocean.com/pricing/droplets): compute/transfer plans and backup options; exact selected configuration unverified.
- [AWS Lightsail pricing](https://aws.amazon.com/lightsail/pricing/): small deployment bundles; exact region/options unverified.
- [AWS pricing calculator](https://calculator.aws/): quote EC2, ALB, transfer, logs, and storage for larger scenarios.
- [Supabase pricing](https://supabase.com/pricing): verify project compute, storage, egress, backups/PITR, and connection limits.
- Domain renewal and staffing rates require your own supplier/internal quotes.

Record region, quote date, billable transfer direction, included allowances, retention policy, recovery point/time objectives, and support level. Load-test representative search/detail/comment traffic and exercise a database restore before committing to capacity.
