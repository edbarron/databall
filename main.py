import os
import datetime
from tabulate import tabulate

from api_databall import get_fixtures_by_date
from config_leagues import TRACKED_LEAGUES
from db_utils import (
    insert_match,
    query_stored_matches,
    export_matches_to_excel,
    get_last_matches_for_team,
    query_matches_by_date,
)
from simulate import simulate_by_day
from utils import get_date_range



# -----------------------------
# Helpers (prompts reutilizables)
# -----------------------------

def clear_screen():
    """Limpia la terminal en Windows/macOS/Linux; fallback ANSI si no hay 'clear/cls'."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        # Fallback ANSI
        print("\033[2J\033[H", end="")

def pause_and_clear():
    input("\n↩️  Presiona Enter para volver al menú...")
    clear_screen()

def _select_period() -> str | None:
    print("\nChoose a time range:")
    print("1. Day")
    print("2. Week")
    print("3. Month")
    print("4. Year")
    choice = input("\n👉 Select a period (1-4): ").strip()
    return {"1": "day", "2": "week", "3": "month", "4": "year"}.get(choice)


def _select_option() -> str | None:
    print("\nChoose a range option:")
    print("1. Current")
    print("2. Last")
    print("3. Custom")
    choice = input("\n👉 Select an option (1-3): ").strip()
    return {"1": "current", "2": "last", "3": "custom"}.get(choice)


def _ask_custom_value(period: str, option: str) -> str | None:
    if option != "custom":
        return None
    if period in ["day", "week"]:
        return input("📅 Enter date (YYYY-MM-DD): ").strip()
    if period == "month":
        return input("📅 Enter month (YYYY-MM): ").strip()
    if period == "year":
        return input("📅 Enter year (YYYY): ").strip()
    return None


def _pick_range_interactively() -> tuple[str, str] | None:
    period = _select_period()
    if not period:
        print("❌ Invalid choice.")
        return None

    option = _select_option()
    if not option:
        print("❌ Invalid option.")
        return None

    custom_value = _ask_custom_value(period, option)
    try:
        start_date, end_date = get_date_range(period, option, custom_value)
        return start_date, end_date
    except ValueError as e:
        print(f"❌ Error: {e}")
        return None


# -----------------------------
# Core features
# -----------------------------
def download_data():
    print("\n📥 [SYNC] Downloading data...")
    picked = _pick_range_interactively()
    if not picked:
        return
    start_date, end_date = picked

    print(f"\n🔎 Fetching matches from {start_date} to {end_date}...")
    all_fixtures = []
    for league in TRACKED_LEAGUES:
        code = league["code"]
        name = league["name"]
        fixtures = get_fixtures_by_date(start_date, end_date, code)
        print(f"→ {name}: {len(fixtures)} matches loaded")
        all_fixtures.extend(fixtures)

    print(f"\n🧾 Total fixtures to insert: {len(all_fixtures)}")

    inserted = 0
    for fixture in all_fixtures:
        match_id = insert_match(fixture)
        if match_id:
            inserted += 1

    print(f"✅ [DONE] Data synced. Inserted {inserted} new matches.")


def view_data():
    print("\n📋 [VIEW] Display stored matches by time range")
    picked = _pick_range_interactively()
    if not picked:
        return
    start_date, end_date = picked

    print(f"\n🔎 Showing matches from {start_date} to {end_date}...")
    matches = query_stored_matches(start_date, end_date)
    if matches:
        print(tabulate(matches, headers="keys", tablefmt="fancy_grid"))
    else:
        print("⚠️ No matches found in that period.")


def export_data():
    print("\n📤 [EXPORT] Exporting data to Excel...")
    picked = _pick_range_interactively()
    if not picked:
        return
    start_date, end_date = picked

    os.makedirs("exports", exist_ok=True)
    default_filename = f"exports/matches_{start_date}_to_{end_date}.xlsx"
    user = input(f"💾 Enter filename (default: {default_filename}): ").strip()

    if not user:
        filename = default_filename
    else:
        if not user.lower().endswith(".xlsx"):
            user += ".xlsx"
        # Si el usuario no puso ruta, guardamos en exports/
        filename = user if os.path.isabs(user) or os.path.dirname(user) else os.path.join("exports", user)

    success = export_matches_to_excel(filename, start_date, end_date)
    if success:
        print(f"\n✅ Data exported successfully to {filename}")
    else:
        print("❌ Failed to export data.")


def simulate_match():
    while True:
        print("\n🔮 [SIMULATE MATCH]")
        print("\n1. Simulate by day")
        print("2. Compare two teams (WIP)")
        print("3. Team stats (WIP)")
        print("4. Team rankings (WIP)")
        print("5. Back to main menu")

        choice = input("\n👉 Select an option (1-5): ").strip()
        if choice == "1":
            simulate_by_day()
        elif choice == "2":
            print("⚔️ Compare two teams is under development.")
        elif choice == "3":
            print("📊 Team stats is under development.")
        elif choice == "4":
            print("🏆 Team rankings is under development.")
        elif choice == "5":
            break
        else:
            print("❌ Invalid choice. Try again.")


def _today_preview() -> str:
    """Devuelve un pequeño resumen de cuántos partidos hay hoy en DB."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        matches = query_matches_by_date(today)
        count = len(matches)
        return f"{count} stored" if count else "none stored"
    except Exception:
        return "unknown"


def main():
    while True:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"\nWelcome to DataBall! ⚽ Today is {today}.")
        print(f"Today matches (in DB): { _today_preview() }.")

        print("\n1. Download data")
        print("2. View stored data")
        print("3. Export data")
        print("4. Simulate match")
        print("5. Exit")

        choice = input("\n👉 Select an option: ").strip()

        if choice == "1":
            download_data()
        elif choice == "2":
            view_data()
        elif choice == "3":
            export_data()
        elif choice == "4":
            simulate_match()
        elif choice == "5":
            print("👋 Exiting Databall. Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
