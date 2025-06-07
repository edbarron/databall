import datetime
from tabulate import tabulate

from api_databall import get_fixtures_by_date  # Ya no necesitas get_match_statistics
from db_utils import insert_match, query_stored_matches, export_matches_to_excel
from utils import get_date_range
from config_leagues import TRACKED_LEAGUES


def download_data():
    print("\n📥 [SYNC] Downloading data...")
    print("\nChoose a time range:")
    print("1. Day")
    print("2. Week")
    print("3. Month")
    print("4. Year")
    period_choice = input("\n👉 Select a period (1-4): ")

    period_map = {"1": "day", "2": "week", "3": "month", "4": "year"}
    period = period_map.get(period_choice)
    if not period:
        print("❌ Invalid choice.")
        return

    print("\nChoose a range option:")
    print("1. Current")
    print("2. Last")
    print("3. Custom")
    option_choice = input("\n👉 Select an option (1-3): ")

    option_map = {"1": "current", "2": "last", "3": "custom"}
    option = option_map.get(option_choice)
    if not option:
        print("❌ Invalid option.")
        return

    custom_value = None
    if option == "custom":
        if period in ["day", "week"]:
            custom_value = input("📅 Enter date (YYYY-MM-DD): ")
        elif period == "month":
            custom_value = input("📅 Enter month (YYYY-MM): ")
        elif period == "year":
            custom_value = input("📅 Enter year (YYYY): ")

    try:
        start_date, end_date = get_date_range(period, option, custom_value)
    except ValueError as e:
        print(f"❌ Error: {e}")
        return

    print(f"\n🔎 Fetching matches from {start_date} to {end_date}...")
    all_fixtures = []

    for league in TRACKED_LEAGUES:
        code = league["code"]
        name = league["name"]
        fixtures = get_fixtures_by_date(start_date, end_date, code)
        print(f"→ {name}: {len(fixtures)} matches loaded")
        all_fixtures.extend(fixtures)

    print(f"\n🧾 Total fixtures to insert: {len(all_fixtures)}")

    match_ids = []
    for fixture in all_fixtures:
        match_id = insert_match(fixture)
        if match_id:
            match_ids.append(match_id)

    print("✅ [DONE] Data synced")


def view_data():
    print("📋 [VIEW] Displaying stored matches")
    matches = query_stored_matches()
    if matches:
        print(tabulate(matches, headers="keys", tablefmt="fancy_grid"))
    else:
        print("⚠️ No matches found in the database.")


def export_data():
    print("📤 [EXPORT] Exporting data to Excel...")
    filename = input("💾 Enter filename (default: matches.xlsx): ").strip()
    if not filename:
        filename = "matches.xlsx"
    success = export_matches_to_excel(filename)
    if success:
        print(f"✅ Data exported successfully to {filename}")
    else:
        print("❌ Failed to export data.")


def main():
    while True:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"\nWelcome to DataBall! ⚽ Today is {today}.")

        print("\n1. Download data")
        print("2. View stored data")
        print("3. Export data")
        print("4. Exit")
        
        choice = input("\n👉 Select an option: ")
        
        if choice == "1":
            download_data()
        elif choice == "2":
            view_data()
        elif choice == "3":
            export_data()
        elif choice == "4":
            print("👋 Exiting Databall. Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
