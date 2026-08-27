# ⚽ DataBall – Football Match Tracker & Simulator (CLI)

A command‑line tool that downloads, stores, displays, and simulates football matches using public APIs.  
It keeps a local SQLite database, shows a 3‑day dashboard (yesterday/today/tomorrow) grouped by league, and lets you export data to Excel.

---

## ✨ Features

- **Data download** – Fetches fixtures for a custom date range (day/week/month/year) from a football API.
- **Local SQLite storage** – Stores matches, teams, and leagues for fast querying.
- **3‑day dashboard** – Shows yesterday/today/tomorrow matches grouped by league with coloured scores.
- **View & filter** – Display stored matches by any date range, grouped by league with league flags.
- **Export to Excel** – Export any date range to a `.xlsx` file.
- **Match simulation** – Simulate match outcomes using custom logic (basic day simulation works).
- **League flags** – Visual flags (emojis) for Premier League, La Liga, Serie A, Brasileirão, Champions League.
- **Colour‑coded scores** – Win = green, loss = red, draw = yellow.

---

## 🛠️ Tech Stack

- Python 3.10+
- SQLite (local database)
- `tabulate` (pretty table output)
- `requests` (API calls)
- `openpyxl` (Excel export)
- `python-dotenv` (environment variables)

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/edbarron/databall.git
   cd databall
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**  
   Create a `.env` file in the root directory:
   ```env
   API_KEY=your_football_api_key
   # BASE_URL=optional_override
   ```
   > **Note:** The tool expects a football API (like API‑Football). Adjust the `api_databall.py` to match your provider.

5. **Initialise the database**
   ```bash
   python -c "from db_init import initialize_database; initialize_database()"
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Description |
| :--- | :--- |
| `API_KEY` | Your football API key (required for downloads). |
| `BASE_URL` | Optional – API base URL (default: `https://v3.football.api-sports.io/`). |

### Tracked Leagues

Edit `config_leagues.py` to add/remove leagues. Each entry requires:
- `code` – league ID from your API provider.
- `name` – display name.

---

## 📊 How It Works

1. **Download** – Fetches fixtures for a given date range using the API.
2. **Store** – Inserts new matches into the SQLite database (deduplicated by fixture ID).
3. **View** – Queries stored matches and displays them grouped by league.
4. **Dashboard** – The main menu automatically shows a compact 3‑day view.
5. **Simulate** – (WIP) Simulates matches based on team statistics.
6. **Export** – Exports any date range to an Excel file with full match details.

---

## 📁 File Structure

```
databall/
├── main.py               # Main menu and UI
├── api_databall.py       # API client (fetch fixtures)
├── db_utils.py           # Database operations (insert, query, export)
├── db_init.py            # Schema initialisation
├── config.py             # Paths, base directories
├── config_leagues.py     # List of tracked leagues
├── simulate.py           # Match simulation logic
├── utils.py              # Date helpers and utilities
├── schema.sql            # SQL schema for tables
├── .env                  # Environment variables (not tracked)
├── .env.example          # Example env file
├── requirements.txt      # Python dependencies
├── databall.db           # SQLite database (auto‑generated)
├── exports/              # Exported Excel files (auto‑created)
└── README.md             # This file
```

---

## 🧪 Testing

Run the tool with a small date range first (e.g., "today") to verify API connectivity and database insertion. Use `DEBUG=True` in your environment to see API responses.

---

## 📄 License

MIT – free to use, modify, and distribute.

---

**Maintainer:** [PxlCode Studio](https://pxlcode.xyz) · [GitHub](https://github.com/edbarron)
