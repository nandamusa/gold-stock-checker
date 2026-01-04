antam-stock-checker-bot

📌 Description
A personal bot that checks Antam gold stock availability and sends notifications to Telegram.

🎯 Purpose
Built for personal use to automatically monitor Antam gold stock without manual checking.

⚙️ How It Works

1. Runs every hour using GitHub Actions (cron)
2. Uses Playwright to check stock availability
3. Sends updates through a Telegram bot
4. Dependencies managed with uv

🧰 Tech Stack

1. Python 3.12
2. Playwright
3. Telegram Bot API
4. uv

🚀 Running the Project
This project is designed to run via GitHub Actions.
Workflow:

1. GitHub Actions triggers on an hourly cron schedule
2. Python environment is set up using uv
3. Stock check script is executed
4. Telegram notification is sent when conditions are met

🛠 Status
✅ Finished
🔧 Maintenance only if improvements are needed

🔒 License
Private project (no license specified)
