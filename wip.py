
"""COM4018 – Equipment Hire Console App

A simple, menu-driven console program for a small shop that hires fishing/camping
equipment. It records hires and prints an earnings report.

Key rules:
- First night: 100% of the listed daily rate (per item).
- Each additional night: +50% of the daily rate (per item, per night).
- If items are returned after 2pm (i.e., not on time), charge one extra "additional night"
  (+50% of the daily rate per item).
- Money is handled as integer pence to avoid floating-point error.
"""

# -----------------------------
# Read-only equipment catalogue (Figure 2)
# -----------------------------
CATALOG = (
    {"code": "DCH", "name": "Day chairs", "daily_p": 1500},   # £15.00
    {"code": "BCH", "name": "Bed chairs", "daily_p": 2500},   # £25.00
    {"code": "BAS", "name": "Bite Alarm (set of 3)", "daily_p": 2000},  # £20.00
    {"code": "BA1", "name": "Bite Alarm (single)", "daily_p": 500},     # £5.00
    {"code": "BBT", "name": "Bait Boat", "daily_p": 6000},    # £60.00
    {"code": "TNT", "name": "Camping tent", "daily_p": 2000}, # £20.00
    {"code": "SLP", "name": "Sleeping bag", "daily_p": 2000}, # £20.00
    {"code": "R3T", "name": "Rods (3lb TC)", "daily_p": 1000},          # £10.00
    {"code": "RBR", "name": "Rods (Bait runners)", "daily_p": 500},     # £5.00
    {"code": "REB", "name": "Reels (Bait runners)", "daily_p": 1000},   # £10.00
    {"code": "STV", "name": "Camping Gas stove (Double burner)", "daily_p": 1000},  # £10.00
)

ADDITIONAL_NIGHT_MULTIPLIER_NUM = 1  # for 50% we add daily_p // 2 per additional night
ADDITIONAL_NIGHT_MULTIPLIER_DEN = 2


# -----------------------------
# App state (no globals)
# -----------------------------
class AppState:
    """Holds mutable program state for the current run."""
    def __init__(self) -> None:
        self.hire_records = []      # list[dict]
        self.next_customer_id = 101 # simple running ID (matches brief samples)


# -----------------------------
# Utilities
# -----------------------------
def money(pence: int) -> str:
    """Format integer pence as '£x,xxx.xx' without thousands separator if not needed."""
    pounds = pence // 100
    pennies = pence % 100
    return f"£{pounds:,}.{pennies:02d}"


def find_item(code: str) -> dict | None:
    """Return catalog item dict by item code (case-insensitive), else None."""
    code = code.upper()
    return next((it for it in CATALOG if it["code"] == code), None)


def catalog_codes() -> str:
    """Return a compact string of known codes for prompts."""
    return ", ".join(it["code"] for it in CATALOG)


def print_main_menu() -> None:
    """Print the main menu (Task 1)."""
    print("\n=== Main Menu ===")
    print("1) Customer & hire details")
    print("2) Earnings report")
    print("3) Exit")


def read_choice() -> int | None:
    """Read a menu choice (1–3). Return int or None if invalid."""
    s = input("Select an option (1-3): ").strip()
    if not s.isdigit():
        return None
    n = int(s)
    return n if n in (1, 2, 3) else None


def read_yes_no(prompt: str = "(y/n): ") -> str:
    """Read 'y' or 'n' (accepts 'yes'/'no'). Returns 'y' or 'n'."""
    while True:
        s = input(prompt).strip().lower()
        if s in ("y", "n", "yes", "no"):
            return "y" if s.startswith("y") else "n"
        print("Please enter 'y' or 'n'.")


def parse_csv_2_fields(line: str) -> tuple[str, str] | None:
    """Parse 'A, B' into two trimmed fields. Supports simple quotes around A or B."""
    line = line.strip()
    if not line:
        return None
    # Simple hand-rolled parser for two fields with optional quotes
    in_quotes = False
    buf = []
    fields: list[str] = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            # toggle quotes or treat doubled "" as literal quote
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                buf.append('"')
                i += 1
            else:
                in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            fields.append("".join(buf).strip())
            buf.clear()
        else:
            buf.append(ch)
        i += 1
    fields.append("".join(buf).strip())

    if len(fields) != 2:
        return None
    return fields[0], fields[1]


def read_positive_int(prompt: str, min_value: int = 1) -> int:
    """Read a positive integer ≥ min_value."""
    while True:
        s = input(prompt).strip()
        if not s.isdigit():
            print("Please enter a whole number.")
            continue
        n = int(s)
        if n < min_value:
            print(f"Please enter a number ≥ {min_value}.")
            continue
        return n


# -----------------------------
# Input: Customer + Hire header (Task 2)
# -----------------------------
def read_customer_header() -> dict | None:
    """Prompt for customer header: name, phone, house_no, postcode, card_last4."""
    print("\nEnter customer (comma separated):")
    print("  name, phone, house_no, postcode, card_last4")
    print("  Example:  Jane Smith, 07900111222, 12, LE1 2AB, 1234")
    s = input("> ").strip()
    if not s:
        print("Cancelled.")
        return None

    fields = parse_csv_2_fields(s)
    # If only two fields detected, retry with simple split by ',' to get 5
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 5:
        print("Expected 5 fields separated by commas.")
        return None

    name, phone, house_no, postcode, card_last4 = parts
    name = name.strip()
    phone_digits = "".join(ch for ch in phone if ch.isdigit())
    card_digits = "".join(ch for ch in card_last4 if ch.isdigit())

    if not name:
        print("Name cannot be empty.")
        return None
    if len(phone_digits) < 7:
        print("Phone should contain at least 7 digits.")
        return None
    if len(card_digits) != 4:
        print("Card last 4 digits must be exactly 4 digits.")
        return None

    return {
        "customer_name": name,
        "phone": phone_digits,
        "house_no": house_no.strip(),
        "postcode": postcode.strip().upper(),
        "card_last4": card_digits,
    }


def calc_line_costs(daily_p: int, qty: int, nights: int,
                    returned_on_time: bool) -> tuple[int, int, int]:
    """Return (first_night_p, additional_p, extra_delay_p) for one line."""
    first_night_p = daily_p * qty
    add_per_night = (daily_p * qty * ADDITIONAL_NIGHT_MULTIPLIER_NUM) // \
                    ADDITIONAL_NIGHT_MULTIPLIER_DEN
    additional_p = add_per_night * max(0, nights - 1)
    extra_delay_p = 0 if returned_on_time else add_per_night
    return first_night_p, additional_p, extra_delay_p


def read_item_lines(nights: int, returned_on_time: bool) -> list[dict]:
    """Read item lines: 'CODE, quantity' (one per line). Returns computed line dicts."""
    print("\nEnter item lines (one per line), then press ENTER on a blank line to finish.")
    print("Format: CODE, quantity   e.g.,  DCH, 2")
    print(f"Nights for this hire: {nights}  | Returned on time: {returned_on_time}")
    print(f"Known codes: {catalog_codes()}")
    lines: list[dict] = []

    while True:
        raw = input("> ").strip()
        if raw == "":
            if not lines:
                print("You must enter at least one item.")
                continue
            return lines

        parsed = parse_csv_2_fields(raw)
        if parsed is None:
            print("Expected 2 fields: CODE, quantity")
            continue

        code_s, qty_s = parsed
        code = code_s.upper()
        item = find_item(code)
        if not item:
            print(f"Unknown code '{code}'. Known: {catalog_codes()}")
            continue
        if not qty_s.isdigit():
            print("Quantity must be a whole number.")
            continue

        qty = int(qty_s)
        if qty < 1:
            print("Quantity must be ≥ 1.")
            continue

        daily = item["daily_p"]
        first_p, add_p, delay_p = calc_line_costs(daily, qty, nights, returned_on_time)
        lines.append({
            "code": code,
            "name": item["name"],
            "qty": qty,
            "daily_p": daily,
            "first_night_p": first_p,
            "additional_nights_p": add_p,
            "extra_delay_p": delay_p,
            "line_total_p": first_p + add_p + delay_p,
        })


# -----------------------------
# Task 2 – Hire flow (with pricing rules)
# -----------------------------
def run_hire_flow(state: AppState) -> None:
    """Run the equipment hire process (Task 2)."""
    while True:
        header = read_customer_header()
        if header is None:
            print("Returning to main menu.")
            return

        nights = read_positive_int("Number of nights: ", min_value=1)
        returned_on_time = (read_yes_no("Returned on time (y/n)? ") == "y")
        lines = read_item_lines(nights, returned_on_time)

        # Summarise line totals
        items_summary = ", ".join(f"{ln['name']} – {ln['qty']}" for ln in lines)
        extra_delay_p = sum(ln["extra_delay_p"] for ln in lines)
        total_p = sum(ln["line_total_p"] for ln in lines)

        hire = {
            "customer_id": state.next_customer_id,
            "customer_name": header["customer_name"],
            "nights": nights,
            "returned_on_time": "y" if returned_on_time else "n",
            "lines": lines,
            "extra_delay_p": extra_delay_p,
            "total_p": total_p,
            "items_summary": items_summary,
        }
        state.hire_records.append(hire)
        state.next_customer_id += 1

        print("\nSaved hire:")
        print(f"  Customer ID: {hire['customer_id']}")
        print(f"  Customer:    {hire['customer_name']}")
        print(f"  Equipment:   {items_summary}")
        print(f"  Nights:      {nights}")
        print(f"  Returned on time: {hire['returned_on_time']}")
        print(f"  Extra charge for delayed return: {money(extra_delay_p)}")
        print(f"  Total cost:  {money(total_p)}\n")

        if read_yes_no("Add another hire (y/n)? ") == "n":
            print("Returning to main menu.")
            return


# -----------------------------
# Task 3B — Earnings report
# -----------------------------
def run_earnings_report(state: AppState) -> None:
    """Print an earnings report similar to Figure 4, plus a TOTAL EARNINGS footer."""
    if not state.hire_records:
        print("\nNo hires recorded yet.")
        return

    print("\n" + "-" * 118)
    print("Earnings Report")
    print("-" * 118)

    header = (
        f"{'ID':<4} | {'Customer Name':<20} | {'Equipment (Name – Qty)':<45} | "
        f"{'Nights':>6} | {'On-Time':>7} | {'Late Fee':>10} | {'Total Cost':>12}"
    )
    print(header)
    print("-" * 118)

    grand_total = 0
    for record in state.hire_records:
        items_summary = record["items_summary"]
        if len(items_summary) > 45:
            items_summary = items_summary[:42] + "..."

        row = (
            f"{record['customer_id']:<4} | "
            f"{record['customer_name']:<20} | "
            f"{items_summary:<45} | "
            f"{record['nights']:>6} | "
            f"{record['returned_on_time']:>7} | "
            f"{money(record['extra_delay_p']):>10} | "
            f"{money(record['total_p']):>12}"
        )
        print(row)
        grand_total += record["total_p"]

    print("-" * 118)
    print(f"{'TOTAL EARNINGS':>100} : {money(grand_total):>15}")


# -----------------------------
# Main loop
# -----------------------------
def main() -> None:
    """Program entry point: menu loop."""
    state = AppState()
    while True:
        print_main_menu()
        choice = read_choice()
        if choice is None:
            print("Invalid option, try again.")
            continue

        if choice == 1:
            run_hire_flow(state)
        elif choice == 2:
            run_earnings_report(state)
        elif choice == 3:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
