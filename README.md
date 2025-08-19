# BCResearch Update — Governance Proposals Tracker (Streamlit)

A lightweight Streamlit app that tracks **L1/L2 improvement proposals** and helps PMs/engineers see potential impact quickly.

* **Sources covered (current):**
  **EIPs** (Ethereum), **BIPs** (Bitcoin), **TIPs** (TRON), **BEPs** (BNB Chain), **SUPs** (Optimism).
* **How it works (current):** **Web scraping** of official sites/GitHub to list latest items, filter by status, and show basic context.
* **Optional:** Slack/email notifications on a **daily** schedule when new proposals appear.

> ⚠️ Note: Real-time L1 metrics and multi-protocol analytics are **planned** but **not yet enabled**.

---

## Demo

* Streamlit app: *(add your deployed link here, e.g. Streamlit Community Cloud)*
  Example: `https://bcresearchupdate-...streamlit.app/`

---

## Features

* ✅ Fetch latest improvement proposals (EIPs/BIPs/TIPs/BEPs/SUPs) via scraping
* ✅ UI to filter/sort and open source pages
* ✅ One-click manual refresh
* ✅ Optional Slack/Email notifications with daily scheduler
* 🚧 Roadmap: Real-time network/market data tiles, impact tags, CSV export, global search

---

## Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python scraping utilities + lightweight schedulers
* **Notifications:** Slack Webhook and/or SMTP email

---

## Quick Start (Local)

```bash
# 1) Clone
git clone https://github.com/nwinnie450/BCResearch_Update.git
cd BCResearch_Update

# 2) (Optional) Create & activate venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3) Install deps
pip install -r requirements.txt

# 4) Run app
streamlit run app.py
```

Open: [http://localhost:8501](http://localhost:8501)

---

## Configuration

Create a `.env` file in the project root. Scraping works without keys, but for notifications add:

```dotenv
# --- OPTIONAL: Slack notifications ---
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ

# --- OPTIONAL: Email notifications ---
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=pm@example.com,dev@example.com

# --- OPTIONAL: GitHub token (for API mode) ---
GITHUB_TOKEN=ghp_...
```

> Check `slack_notification_system.py`, `enhanced_notification_system.py`, and `unified_notification_system.py` for exact env usage.

---

## How to Use

1. **Launch** → Home shows latest proposals grouped by ecosystem
2. **Filter** by status and click through to originals
3. **Refresh** manually (top bar button)
4. **Enable notifications (optional):**

   * Add env vars above
   * Run scheduler script

---

## Notifications & Scheduler

* **Slack:** Compact digest via Incoming Webhook
* **Email:** Same digest over SMTP
* **Schedule:** Default is **once per day**

Run helpers:

```bash
# Start a daily scheduler
python start_scheduler.py

# Test Slack
python trigger_test_notification.py --channel slack

# Test Email
python trigger_test_notification.py --channel email
```

Or demo:

```bash
python demo_16_30_schedule.py
```

---

## Project Structure

```
.
├─ app.py                    # Streamlit UI
├─ services/                 # Scrapers & data handling
├─ scripts/                  # Scheduler/test scripts
├─ slack_notification_system.py
├─ enhanced_notification_system.py
├─ unified_notification_system.py
├─ .streamlit/               # Streamlit config
├─ styles/                   # CSS helpers
└─ .env.example              # Sample env
```

---

## Data Sources

* **EIPs:** [https://eips.ethereum.org/all](https://eips.ethereum.org/all)
* **BIPs:** [https://bips.dev/](https://bips.dev/)
* **TIPs:** [https://github.com/tronprotocol/tips/issues](https://github.com/tronprotocol/tips/issues)
* **BEPs:** [https://github.com/bnb-chain/BEPs](https://github.com/bnb-chain/BEPs)
* **SUPs:** [https://github.com/ethereum-optimism/SUPs](https://github.com/ethereum-optimism/SUPs)

*(Scraping mode avoids API rate limits; GitHub API possible with token.)*

---

## Roadmap

* [ ] Real-time L1 metrics (TPS, fees, throughput)
* [ ] Per-proposal **Impact Tags** (e.g., consensus, dev tooling)
* [ ] CSV/JSON export & Slack thread formatting
* [ ] “What changed since yesterday?” diff view
* [ ] Mobile-friendly UI

---

## Troubleshooting

* **401 GitHub API?** Add `GITHUB_TOKEN`
* **No Slack msg?** Check `SLACK_WEBHOOK_URL` + scheduler
* **Email failed?** Use app-specific password, verify TLS/port

---

## Contributing

PRs welcome! Focus on reliability of scraping + UI clarity.

---

## License

MIT
