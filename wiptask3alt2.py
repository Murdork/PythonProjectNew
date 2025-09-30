"""COM4018 – Equipment Hire Console App (Tasks 1, 2 & 3)

A simple, menu-driven console program for a small shop that hires fishing/camping

This file contains the final, complete implementation for all tasks.
"""

# -----------------------------
# Read-only equipment catalogue (Figure 2)
# -----------------------------

# -----------------------------
# Equipment catalogue (read-only): prices stored in integer pence
# to avoid floating-point rounding issues during calculations.
# -----------------------------
CATALOG = (
    {"code": "DCH", "name": "Day chairs", "daily_p": 1500},
    {"code": "BCH", "name": "Bed chairs", "daily_p": 2500},
    {"code": "BAS", "name": "Bite Alarm (set of 3)", "daily_p": 2000},
    {"code": "BA1", "name": "Bite Alarm (single)", "daily_p": 500},
    {"code": "BBT", "name": "Bait Boat", "daily_p": 6000},
    {"code": "TNT", "name": "Camping tent", "daily_p": 2000},
    {"code": "SLP", "name": "Sleeping bag", "daily_p": 2000},
    {"code": "R3T", "name": "Rods (3lb TC)", "daily_p": 1000},
    {"code": "RBR", "name": "Rods (Bait runners)", "daily_p": 500},
    {"code": "REB", "name": "Reels (Bait runners)", "daily_p": 1000},
    {"code": "STV", "name": "Camping Gas stove (Double burner)", "daily_p": 1000},
)

# -----------------------------
# Pricing rules (per brief):
#  • First night charged at 100% of daily rate.
#  • Each additional night charged at 50% of daily rate.
#  • If returned after 2pm, add one extra 50% night.
# Using a rational (num/den) keeps the 1/2 factor explicit.
# -----------------------------
ADDITIONAL_NIGHT_MULTIPLIER_NUM = 1
ADDITIONAL_NIGHT_MULTIPLIER_DEN = 2


# -----------------------------
# Application state container:
#  • hire_records: list of persisted hire dicts used for the report
#  • next_customer_id: running ID to match sample outputs
# -----------------------------
class AppState:
    """Holds mutable program state for the current run."""
    def __init__(self) -> None:
        self.hire_records = []
        self.next_customer_id = 101


# -----------------------------
# Utilities
# -----------------------------

# Utility: format integer pence as a Sterling string '£x.xx'.
def money(pence: int) -> str:
    pounds = pence // 100
    pennies = pence % 100
    return f"£{pounds}.{pennies:02d}"

# Utility: case-insensitive lookup of a catalogue item by code.
def find_item(code: str) -> dict | None:
    code = code.upper()
    return next((it for it in CATALOG if it["code"] == code), None)

# Utility: comma-separated list of valid item codes for prompts.
def catalog_codes() -> str:
    return ", ".join(it["code"] for it in CATALOG)

# UI: Task 1 menu printed exactly as specified in the brief.
def print_main_menu() -> None:
    print("\n=== Main Menu ===")
    print("1) Enter details of customer and equipment hired")
    print("2) Create report")
    print("3) Exit")

# Input: read and validate a menu choice in the range 1–3.
def read_choice() -> int | None:
    s = input("Select an option (1-3): ").strip()
    if not s.isdigit():
        return None
    n = int(s)
    return n if n in (1, 2, 3) else None

# Input: normalise 'yes'/'no' answers to canonical 'y' or 'n'.
def read_yes_no(prompt: str = "(y/n): ") -> str:
    while True:
        s = input(prompt).strip().lower()
        if s in ("y", "n", "yes", "no"):
            return "y" if s.startswith("y") else "n"
        print("Please enter 'y' or 'n'.")

# Input: read a positive integer (re-prompts until valid).
def read_positive_int(prompt: str, min_value: int = 1) -> int:
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
# Task 2 – Customer header + items
# -----------------------------

# Task 2: prompt for name, phone, house_no, postcode, card_last4.
# Minimal validation applied; values are normalised for storage.
def read_customer_header() -> dict | None:
    print("\nEnter customer (comma separated):")
    print("  name, phone, house_no, postcode, card_last4")
    print("  Example:  Jane Smith, 07900111222, 12, LE1 2AB, 1234")
    s = input("> ").strip()
    if not s:
        print("Cancelled.")
        return None

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

# Pricing: compute first night, additional nights (50%), and any late
# return charge (extra 50% night). Returns totals in pence.
def calc_line_costs(daily_p: int, qty: int, nights: int,
                    returned_on_time: bool) -> tuple[int, int, int]:
    first_night_p = daily_p * qty
    add_per_night = (daily_p * qty * ADDITIONAL_NIGHT_MULTIPLIER_NUM) // \
                    ADDITIONAL_NIGHT_MULTIPLIER_DEN
    additional_p = add_per_night * max(0, nights - 1)
    extra_delay_p = 0 if returned_on_time else add_per_night
    return first_night_p, additional_p, extra_delay_p

# Task 2: collect item lines 'CODE, quantity'; validate and compute
# per-line totals eagerly so later reporting is a simple sum.
def read_item_lines(nights: int, returned_on_time: bool) -> list[dict]:
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

        parts = [p.strip() for p in raw.split(',')]
        if len(parts) != 2:
            print("Expected 2 fields: CODE, quantity")
            continue

        code_s, qty_s = parts
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


# Task 2: interactive hire entry loop; persists a summary record to state.
def run_hire_flow(state: AppState) -> None:
    while True:
        header = read_customer_header()
        if header is None:
            print("Returning to main menu.")
            return

        nights = read_positive_int("Number of nights: ", min_value=1)
        returned_on_time = (read_yes_no("Returned on time (y/n)? ") == "y")
        lines = read_item_lines(nights, returned_on_time)

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


# Task 3: earnings report routine (placeholder in Task 2 variant).
def run_earnings_report(state: AppState) -> None:
    if not state.hire_records:
        print("\nNo hires recorded yet.")
        return

    print("\n=== Earnings Report ===")
    grand_total = 0
    grand_delay = 0

    for hire in state.hire_records:
        print(f"Customer {hire['customer_id']} – {hire['customer_name']}")
        print(f"  Items:  {hire['items_summary']}")
        print(f"  Total:  {money(hire['total_p'])}")
        print(f"  Delay:  {money(hire['extra_delay_p'])}")
        print()
        grand_total += hire['total_p']
        grand_delay += hire['extra_delay_p']

    print("--- Totals ---")
    print(f"Grand total earnings: {money(grand_total)}")
    print(f"Of which late-return charges: {money(grand_delay)}")


# -----------------------------
# Main loop
# -----------------------------

# Entry point: menu loop routes to hire flow, report, or exit.
def main() -> None:
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
