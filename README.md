# Gold Stock Checker �

A high-performance, asynchronous monitoring framework designed to track asset availability and inventory shifts across distributed logistics nodes.

## 🌟 Key Features

- **Asynchronous Execution**: Leverages `asyncio` to monitor multiple inventory nodes concurrently for maximum efficiency.
- **Advanced Request Impersonation**: Uses `curl_cffi` to mimic secure browser environments, ensuring reliable connectivity.
- **Automated Alerting**: Real-time integration with Telegram for instant inventory availability reports.
- **Robust Failover**: Built-in exponential backoff and retry logic powered by `tenacity`.
- **Infrastructure Ready**: Comprehensive support for secure proxying and containerized deployments.
- **Structured Observation**: Professional-grade logging with `structlog` for clear operational insights.

## 🛠️ Tech Stack

- **Core**: Python 3.12+
- **Network**: `curl_cffi` (impersonate Chrome)
- **Parsing**: `selectolax` (LSS-based high-speed HTML extraction)
- **Hardening**: `tenacity` (retry logic), `python-dotenv`
- **Management**: Managed via `uv` for lightning-fast dependency resolution.

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nandamusa/gold-stock-checker.git
   cd gold-stock-checker
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory:
   ```env
   BASE_URL=https://your-target-endpoint.com
   TELEGRAM_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=chat_id1,chat_id2
   PROXY=http://user:pass@host:port  # Optional
   ```

### Configuration

Check `config.py` to define your logic nodes and specific API endpoints:
```python
LOCATION_MAP = {
    "node_primary": "NODE_ID_1",
    "node_secondary": "NODE_ID_2",
}
```

## 📈 Usage

Simply run the main synchronization script:
```bash
python main.py
```

### Automation (GitHub Actions)

This project is built to support serverless execution via GitHub Actions. A sample workflow is available in `.github/workflows/` (if configured) to trigger hourly synchronizations.

## 🔒 License

Distributed under the MIT License. See `LICENSE` for more information.

### Disclaimer
This tool is for educational purposes only. I am not responsible for how you use this software. Users are responsible for complying with local laws and the Terms of Service of the websites being scraped.