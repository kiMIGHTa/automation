# Business Automation Toolkit

A Python automation tool for handling repetitive business admin work — scheduled data exports, formatted Excel reporting, and email/SMS marketing campaigns.

## What it does

- **Data export** — pulls customer, agent, and inventory data from a SQLite database and exports it to a styled Excel workbook (bold colored headers, auto-sized columns), with automatic fallback to sample data if the database is unavailable
- **Email** — sends individual or bulk emails via SMTP, with optional file attachments (e.g. attaching the exported Excel report)
- **SMS** — sends individual or bulk SMS messages via the BulkSMS API
- **Marketing campaigns** — sends a combined email + SMS promotional blast to a customer list in a single call
- **Scheduling** — runs recurring tasks automatically: a daily data export (9 AM) and a weekly marketing campaign (Mondays, 10 AM)
- **Config-driven** — all credentials and settings load from `config.json`, with a default template auto-generated on first run if one doesn't exist

## Setup

1. Clone the repo and install dependencies:
```bash
   pip install pandas openpyxl schedule requests
```

2. Run the script once to generate a default `config.json`, or copy `config.example.json` to `config.json`:
```bash
   cp config.example.json config.json
```

3. Fill in your actual credentials in `config.json`:
   - **Email**: Gmail SMTP address + an [app password](https://support.google.com/accounts/answer/185833) (not your regular password)
   - **SMS**: your BulkSMS API username, password, and endpoint URL
   - **Export**: the local directory where Excel reports should be saved

4. (Optional) Set up a `business_automation.db` SQLite database with `customers`, `agents`, and `inventory` tables matching the schema in `create_sample_data()`. Without a database, the script falls back to bundled sample data automatically.

⚠️ **`config.json` contains real credentials once filled in — it's git-ignored by default and should never be committed.**

## Usage

```python
from business_automation import BusinessAutomation

automation = BusinessAutomation()

# Send a single email
automation.send_email("recipient@example.com", "Subject", "Body text")

# Send a single SMS
automation.send_sms("+254700000000", "Message text")

# Export current data to a formatted Excel file
filepath = automation.auto_export_data()

# Send a marketing campaign to all customers
customer_data, _, _ = automation.create_sample_data()
automation.send_marketing_campaign(customer_data)

# Start the scheduler (runs daily exports + weekly campaigns automatically)
automation.schedule_automated_tasks()
automation.run_scheduler()
```

## Stack

Python · pandas · openpyxl · smtplib · SQLite · BulkSMS API

## Notes

This was built as a freelance utility for automating recurring reporting and outreach tasks that would otherwise be done manually on a schedule. The database layer is swappable — any source that can populate the `customer_data` / `agent_data` / `inventory_data` dict shape will work with the existing export and campaign logic.
