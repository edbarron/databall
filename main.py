import os
from config import BASE_DIR
import datetime
import textwrap
from tabulate import tabulate
from collections import defaultdict
import sys
from api_databall import get_fixtures_by_date
from config_leagues import TRACKED_LEAGUES
from db_utils import (
    insert_match,
    query_stored_matches,
    export_matches_to_excel,
    query_matches_by_date,
    get_connection,
)
from db_init import initialize_database
from simulate import simulate_by_day
from utils import get_date_range


# -----------------------------
# UI helpers
# -----------------------------
def clear_screen():
    """Limpia la terminal en Windows/macOS/Linux; fallback ANSI si no hay 'clear/cls'."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        print("\033[2J\033[H", end="")

def pause_and_clear():
    input("\n↩️  Presiona Enter para volver al menú...")
    clear_screen()

def ensure_db_initialized():
    """Crea las tablas si no existen (usa schema.sql)."""
    try:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            names = {r[0] for r in rows}
            required = {"leagues", "teams", "matches"}
            if not required.issubset(names):
                print("🛠 Initializing database schema...")
                initialize_database()
    except Exception:
        # Si algo falla al checar, intentamos inicializar
        initialize_database()

# -----------------------------
# Prompts reutilizables
# -----------------------------
def _select_period():
    print("\nChoose a time range:")
    print("1. Day")
    print("2. Week")
    print("3. Month")
    print("4. Year")
    choice = input("\n👉 Select a period (1-4): ").strip()
    return {"1": "day", "2": "week", "3": "month", "4": "year"}.get(choice)

def _select_option():
    print("\nChoose a range option:")
    print("1. Current")
    print("2. Last")
    print("3. Custom")
    choice = input("\n👉 Select an option (1-3): ").strip()
    return {"1": "current", "2": "last", "3": "custom"}.get(choice)

def _ask_custom_value(period, option):
    if option != "custom":
        return None
    if period in ["day", "week"]:
        return input("📅 Enter date (YYYY-MM-DD): ").strip()
    if period == "month":
        return input("📅 Enter month (YYYY-MM): ").strip()
    if period == "year":
        return input("📅 Enter year (YYYY): ").strip()
    return None

def _pick_range_interactively():
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

def _normalize_league_name(name: str) -> str:
    import unicodedata
    if not name:
        return ""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_only.strip().lower()

# Ahora usamos la función para generar las claves normalizadas del diccionario
LEAGUE_FLAG_BY_KEY = {
    _normalize_league_name("Premier League"): "⬜⬜🟥⬜⬜\n🟥🟥🟥🟥🟥\n⬜⬜🟥⬜⬜",
    _normalize_league_name("La Liga"): "🟥🟥🟥🟥🟥\n🟨🟥🟨🟨🟨\n🟥🟥🟥🟥🟥",
    _normalize_league_name("Primera Division"): "🟥🟥🟥🟥🟥\n🟨🟥🟨🟨🟨\n🟥🟥🟥🟥🟥",
    _normalize_league_name("Serie A"): "🟩🟩⬜🟥🟥\n🟩🟩⬜🟥🟥\n🟩🟩⬜🟥🟥",
    _normalize_league_name("Campeonato Brasileiro Série A"): "🟩🟩🟨🟩🟩\n🟩🟨🟦🟨🟩\n🟩🟩🟨🟩🟩",
    _normalize_league_name("Campeonato Brasileiro"): "🟩🟩🟨🟩🟩\n🟩🟨🟦🟨🟩\n🟩🟩🟨🟩🟩",
    _normalize_league_name("UEFA Champions League"): "🟦🟦⭐🟦🟦\n🟦⭐🟦⭐🟦\n🟦🟦⭐🟦🟦",
}

def _league_flag(name: str) -> str:
    key = _normalize_league_name(name)
    flag = LEAGUE_FLAG_BY_KEY.get(key)
    return flag or "🌍"

def _short_team(name: str, limit: int = 14) -> str:
    """
    Trunca el nombre de un equipo a `limit` caracteres (incluyendo espacios),
    respetando palabras completas cuando es posible. Si una sola palabra
    ya supera el límite, corta a lo bruto y agrega '…'.

    Esto es puramente cosmético para que tabulate no desencaje la tabla
    con nombres largos (ej. "Real Racing club de santander" -> "Real Racing…").
    El nombre original en la DB no se modifica.
    """
    if not name:
        return ""
    name = name.strip()
    if len(name) <= limit:
        return name
    try:
        return textwrap.shorten(name, width=limit, placeholder="…")
    except ValueError:
        # Ocurre si ni siquiera la primera palabra + "…" entra en el límite
        return name[: limit - 1].rstrip() + "…"

def print_matches_grouped_compact(matches, show_date=True, tablefmt="fancy_grid", color=True):
    """
    Agrupa por liga y muestra Date | Home | Score | Away con estilo:
    - Encabezado por liga con bandera y color
    - Score coloreado (ganador verde, perdedor rojo, empate amarillo)
    - Respeta NO_COLOR y solo colorea si la salida es TTY (o FORCE_COLOR=1)
    """
    # Activar color sólo si: color==True, salida a TTY, NO_COLOR no está definido
    use_color = bool(color) and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    if os.environ.get("FORCE_COLOR"):
        use_color = True

    # Paleta ANSI
    if use_color:
        GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"
        BOLD, DIM = "\033[1m", "\033[2m"
        GOLD = "\033[93m"   # dorado para título de liga
    else:
        GREEN = RED = YELLOW = RESET = BOLD = DIM = GOLD = ""

    def fmt_score(hg, ag):
        if hg is None or ag is None:
            return "---"
        if hg > ag:
            c_home, c_away = GREEN, RED
        elif ag > hg:
            c_home, c_away = RED, GREEN
        else:
            c_home = c_away = YELLOW
        return f"{c_home}{hg}{RESET}-{c_away}{ag}{RESET}"

    # Agrupar por liga
    groups = defaultdict(list)
    for m in matches:
        groups[m["league"]].append(m)

    # Imprimir por liga
    for league in sorted(groups.keys()):
        flag = _league_flag(league)
        count = len(groups[league])
        print(f"\n{GOLD}{flag} {league} {DIM}({count}){RESET}")

        rows = []
        for m in sorted(groups[league], key=lambda x: (x["date"], x["home_team"])):
            score = fmt_score(m.get("home_goals"), m.get("away_goals"))
            home_name = _short_team(m["home_team"])
            away_name = _short_team(m["away_team"])
            row = {"Home": f"{BOLD}{home_name}{RESET}", "Score": score, "Away": away_name}
            if show_date:
                row = {"Date": m["date"], **row}
            rows.append(row)

        print(tabulate(rows, headers="keys", tablefmt=tablefmt) if rows else "(no matches)")

def render_three_day_dashboard():
    """Muestra, por liga, los partidos de Ayer/Hoy/Mañana."""
    # Fechas (cadena YYYY-MM-DD)
    today_date = datetime.datetime.now().date()
    yesterday_date = today_date - datetime.timedelta(days=1)
    tomorrow_date = today_date + datetime.timedelta(days=1)
    today = today_date.strftime("%Y-%m-%d")
    yesterday = yesterday_date.strftime("%Y-%m-%d")
    tomorrow = tomorrow_date.strftime("%Y-%m-%d")

    try:
        # Traemos todo el rango de una sola vez
        matches = query_stored_matches(yesterday, tomorrow)
    except Exception as e:
        print(f"\n⚠️ Could not load matches: {e}")
        return

    # Color ANSI: respeta TTY/NO_COLOR/FORCE_COLOR
    use_color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    if os.environ.get("FORCE_COLOR"):
        use_color = True
    if use_color:
        GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"
        BOLD, DIM, GOLD, CYAN = "\033[1m", "\033[2m", "\033[93m", "\033[96m"
    else:
        GREEN = RED = YELLOW = RESET = BOLD = DIM = GOLD = CYAN = ""

    def fmt_score(hg, ag):
        if hg is None or ag is None:
            return "---"
        if hg > ag:
            ch, ca = GREEN, RED
        elif ag > hg:
            ch, ca = RED, GREEN
        else:
            ch = ca = YELLOW
        return f"{ch}{hg}{RESET}-{ca}{ag}{RESET}"

    # Agrupar: league → {yesterday[], today[], tomorrow[]}
    buckets = defaultdict(lambda: {"yesterday": [], "today": [], "tomorrow": []})
    for m in matches or []:
        d = m.get("date")
        if d == yesterday:
            key = "yesterday"
        elif d == today:
            key = "today"
        elif d == tomorrow:
            key = "tomorrow"
        else:
            continue
        buckets[m["league"]][key].append(m)

    # Orden y render
    labels = [
        ("yesterday", f"Yesterday ({yesterday})"),
        ("today",     f"Today ({today})"),
        ("tomorrow",  f"Tomorrow ({tomorrow})"),
    ]

    if not buckets:
        print("\nNo matches for Yesterday/Today/Tomorrow.")
        return

    for league in sorted(buckets.keys()):
        tri = buckets[league]
        total = sum(len(v) for v in tri.values())
        print(f"\n{GOLD}{_league_flag(league)} {league} {DIM}({total}){RESET}")

        for key, title in labels:
            items = sorted(tri[key], key=lambda x: (x.get("date"), x.get("home_team") or ""))
            print(f"\n{CYAN}{title}{RESET}")
            if not items:
                print("(no matches)")
                continue
            rows = []
            for m in items:
                rows.append({
                    "\033[94mHome\033[0m": f"{BOLD}{_short_team(m['home_team'])}{RESET}",
                    "\033[94mScore\033[0m": fmt_score(m.get("home_goals"), m.get("away_goals")),
                    "\033[94mAway\033[0m": _short_team(m["away_team"]),
                })
            print(tabulate(rows, headers="keys", tablefmt="fancy_grid"))



# -----------------------------
# Core features
# -----------------------------
def download_data():
    clear_screen()
    print("\n📥 [SYNC] Downloading data...")
    picked = _pick_range_interactively()
    if not picked:
        pause_and_clear()
        return
    start_date, end_date = picked

    print(f"\n🔎 Fetching matches from {start_date} to {end_date}...")
    all_fixtures = []
    try:
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
    except Exception as e:
        print(f"❌ Sync failed: {e}")
    finally:
        pause_and_clear()

def view_data():
    print("\n📋 [VIEW] Display stored matches by time range")
    picked = _pick_range_interactively()
    if not picked:
        return
    start_date, end_date = picked

    print(f"\n🔎 Showing matches from {start_date} to {end_date}...")
    matches = query_stored_matches(start_date, end_date)
    if matches:
        # Compacto: solo equipos y marcador, agrupado por liga (sin id ni league).
        print_matches_grouped_compact(matches, show_date=True, tablefmt="fancy_grid", color=True)
        input("\nPress Enter to return to the main menu...")
    else:
        print("⚠️ No matches found in that period.")
        input("\nPress Enter to return to the main menu...")

def export_data():
    clear_screen()
    print("\n📤 [EXPORT] Exporting data to Excel...")
    picked = _pick_range_interactively()
    if not picked:
        pause_and_clear()
        return
    start_date, end_date = picked

    try:
        # Siempre exporta dentro del proyecto
        exports_dir = os.path.join(BASE_DIR, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        default_filename = os.path.join(exports_dir, f"matches_{start_date}_to_{end_date}.xlsx")
        user = input(f"💾 Enter filename (default: {default_filename}): ").strip()

        if not user:
            filename = default_filename
        else:
            # si el usuario no puso ruta absoluta ni carpeta, lo guardamos en /exports del proyecto
            if not os.path.isabs(user) and not os.path.dirname(user):
                user = os.path.join(exports_dir, user)
            if not user.lower().endswith(".xlsx"):
                user += ".xlsx"
            filename = user

        abs_path = os.path.abspath(filename)
        success = export_matches_to_excel(abs_path, start_date, end_date)

        if success:
            print(f"\n✅ Data exported successfully to {abs_path}")
            if not os.path.exists(abs_path):
                print("⚠️ Warning: file not found after export — check permissions.")
        else:
            print("❌ Failed to export data.")
    except Exception as e:
        print(f"❌ Export failed: {e}")
    finally:
        pause_and_clear()

def simulate_match():
    while True:
        clear_screen()
        print("\n🔮 [SIMULATE MATCH]")
        print("\n1. Simulate by day")
        print("2. Compare two teams (WIP)")
        print("3. Team stats (WIP)")
        print("4. Team rankings (WIP)")
        print("5. Back to main menu")

        choice = input("\n👉 Select an option (1-5): ").strip()
        if choice == "1":
            try:
                simulate_by_day()
            except Exception as e:
                print(f"❌ Simulation failed: {e}")
            finally:
                pause_and_clear()
        elif choice == "2":
            print("⚔️ Compare two teams is under development.")
            pause_and_clear()
        elif choice == "3":
            print("📊 Team stats is under development.")
            pause_and_clear()
        elif choice == "4":
            print("🏆 Team rankings is under development.")
            pause_and_clear()
        elif choice == "5":
            break
        else:
            print("❌ Invalid choice. Try again.")
            pause_and_clear()

def _today_preview():
    """Pequeño resumen de cuántos partidos hay hoy en DB."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        matches = query_matches_by_date(today)
        return f"{len(matches)} stored" if matches else "none stored"
    except Exception:
        return "unknown"

# -----------------------------
# Main loop
# -----------------------------

def main():
    ensure_db_initialized()
    while True:
        clear_screen()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"\n\033[92mWelcome to DataBall! ⚽ Today is \033[91m{today}\033[92m.\033[0m")

        # NUEVO: dashboard por liga de Ayer/Hoy/Mañana
        render_three_day_dashboard()
        
        print("\n\033[94mMain Menu\033[0m")
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
            pause_and_clear()

if __name__ == "__main__":
    main()