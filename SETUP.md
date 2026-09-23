# Gagrove Automation V2

Cloud-first automation for the Gagrove Facebook Page.

Flow:
GitHub Actions cloud runner -> Malawi news RSS -> deduplicate/corroborate -> AI editor layer -> branded image -> Meta Graph API -> Facebook Page.

No Docker, n8n, Canva, CapCut, or always-on laptop is required.

Schedule: 07:00, 12:00, 17:00 Africa/Blantyre.

Manual runs can accept a topic. Blank topic uses `Malawi current breaking news`.

Secrets:
- META_PAGE_ID
- META_PAGE_ACCESS_TOKEN
- GEMINI_API_KEY

The included simulation never contacts Facebook and uses fixture news only.


## AI editor (live mode)

When `GEMINI_API_KEY` is present, the production run sends only the selected source evidence to Gemini's structured-output API. The model is instructed not to introduce facts outside that evidence. The code validates that returned source URLs belong to the selected evidence.

Default model: `gemini-3.5-flash-lite`, chosen for high-volume, cost-sensitive automation. You can override it with the `GEMINI_MODEL` secret/environment variable.

The simulation does not call Gemini and does not consume API quota.
