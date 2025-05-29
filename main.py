import datetime
from tabulate import tabulate

from api_databall import get_fixtures_by_date, get_match_statistics
from db_utils import insert_match, insert_match_statistics

# Placeholder: Download and store data based on a given date
def download_data():
    print("\n📥 [SYNC] Downloading data...")
    date_str = input("📅 Enter date (YYYY-MM-DD) or press Enter for today: ")
    if not date_str:
        date_str = datetime.date.today().isoformat()
    print(f"🔎 Fetching matches for {date_str}...")
    # fixtures = get_fixtures_by_date(date_str)
    # for fixture in fixtures:
    #     insert_match(...)  # Placeholder for inserting each match

    print("📊 Fetching statistics for matches...")
    # for match_id in match_ids:
    #     stats = get_match_statistics(match_id)
    #     insert_match_statistics(...)  # Placeholder for inserting stats

    print("✅ [DONE] Data synced (placeholder)")

# Placeholder: View stored data
def view_data():
    print("📋 [VIEW] Displaying stored matches (placeholder)")
    # rows = query_stored_matches()
    # print(tabulate(rows, headers="keys"))

# Placeholder: Export data to Excel
def export_data():
    print("📤 [EXPORT] Exporting data to Excel (placeholder)")
    # export_to_excel()

# CLI Menu
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
