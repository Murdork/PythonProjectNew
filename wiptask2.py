"""COM4018 – Introduction to Programming
Task 2: Hiring equipment (Option 1 flow)

A menu-driven console programme for a small shop that hires fishing/camping equipment.

Design notes:
- Monetary values are stored as integer pence to avoid floating-point rounding issues.
- Pricing rules: first night at 100%; each additional night at 50%; late returns incur one extra 50% night.
- Parsing is split into pure functions (which raise ValueError) and interactive readers (which loop with messages).
- No imports used.
"""

# ---------------- User-facing instructional text ----------------

CUSTOMER_ENTRY_INSTRUCTIONS = (
    "\nEnter customer (comma separated):\n"
    "  name, phone, house_no, postcode, card_last4\n"
    "  Example:  Jane Smith, 07900111222, 12, LE1 2AB, 1234"
)

ITEM_LINES_INSTRUCTIONS = (
    "\nEnter item lines (one per line), then press ENTER on a blank line to finish.\n"
    "Format: CODE, quantity   e.g.,  DCH, 2"
)

MAIN_MENU_LINES = (
    "\n=== Main Menu (Task 2) ===",
    "1) Enter details of customer and equipment hired",
    "2) (Task 3) Create report  [not implemented in Task 2]",
    "3) Exit",
)

PROMPT_SELECT_OPTION = "Select an option (1-3): "

# ---------------- Catalogue & pricing ----------------

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

# 50% multiplier encoded as a rational for clarity
ADDITIONAL_NIGHT_MULTIPLIER_NUM = 1
ADDITIONAL_NIGHT_MULTIPLIER_DEN = 2


class AppState:
    """Holds mutable programme state for the current run (Task 2 focuses on option 1)."""
    def __init__(self) -> None:
        self.hire_records: list[dict] = []
        self.next_customer_id: int = 101


# ---------------- Utilities ----------------

def money(pence: int) -> str:
    """Return integer pence as a sterling string '£x.xx'."""
    pounds = pence // 100
    pennies = pence % 100
    return f"£{pounds}.{pennies:02d}"


def find_item(code: str) -> dict | None:
    """Return the catalogue entry for code (case-insensitive) or None."""
    code = str(code).upper()
    for it in CATALOG:
        if it["code"] == code:
            return it
    return None


def catalog_codes() -> str:
    """Return a comma-separated list of known item codes."""
    return ", ".join(it["code"] for it in CATALOG)


def print_main_menu() -> None:
    """Display the main menu (Task 2 emphasises option 1)."""
    for line in MAIN_MENU_LINES:
        print(line)


def read_choice() -> int | None:
    """Return a validated menu choice (1–3) or None when invalid."""
    s = input(PROMPT_SELECT_OPTION).strip()
    try:
        n = int(s)
    except ValueError:
        return None
    return n if n in (1, 2, 3) else None


def read_yes_no(prompt: str = "(y/n): ") -> bool:
    """Prompt until the user enters yes/no; return True for yes, False for no."""
    while True:
        s = input(prompt).strip().lower()
        if s in ("y", "yes"):
            return True
        if s in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def read_positive_int(prompt: str, min_value: int = 1) -> int:
    """Return a positive integer ≥ min_value after repeated prompting."""
    while True:
        s = input(prompt).strip()
        try:
            n = int(s)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if n < min_value:
            print(f"Please enter a number ≥ {min_value}.")
            continue
        return n


# ---------------- Pure parsers (raise on error) ----------------

def _parse_customer_header(raw: str) -> dict:
    """Parse and normalise the comma-separated customer header string.

    Expected: name, phone, house_no, postcode, card_last4
    Raises ValueError on invalid input.
    """
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 5:
        raise ValueError("Expected 5 fields separated by commas.")

    name, phone, house_no, postcode, card_last4 = parts
    if not name:
        raise ValueError("Name cannot be empty.")

    phone_digits = "".join(ch for ch in phone if ch.isdigit())
    if len(phone_digits) < 7:
        raise ValueError("Phone should contain at least 7 digits.")

    card_digits = "".join(ch for ch in card_last4 if ch.isdigit())
    if len(card_digits) != 4:
        raise ValueError("Card last 4 digits must be exactly 4 digits.")

    return {
        "customer_name": name.strip(),
        "phone": phone_digits,
        "house_no": house_no.strip(),
        "postcode": postcode.strip().upper(),
        "card_last4": card_digits,
    }


def _parse_item_line(raw: str) -> tuple[str, int]:
    """Return (code, qty) parsed from raw, or raise ValueError."""
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 2:
        raise ValueError("Expected 2 fields: CODE, quantity")

    code_s, qty_s = parts
    code = code_s.upper()
    item = find_item(code)
    if not item:
        raise ValueError(f"Unknown code '{code}'. Known: {catalog_codes()}")

    try:
        qty = int(qty_s)
    except ValueError as exc:
        raise ValueError("Quantity must be a whole number.") from exc

    if qty < 1:
        raise ValueError("Quantity must be ≥ 1.")

    return code, qty


# ---------------- Interactive readers (loop + messages) ----------------

def read_customer_header() -> dict | None:
    """Prompt repeatedly for customer fields or return None if cancelled."""
    print(CUSTOMER_ENTRY_INSTRUCTIONS)
    print("Type 'cancel' to return to the menu without saving.")
    while True:
        raw = input("> ").strip()
        if raw.lower() in {"", "cancel"}:
            print("Cancelled.")
            return None
        try:
            return _parse_customer_header(raw)
        except ValueError as err:
            print(err)


def calc_line_costs(daily_p: int, qty: int, nights: int, returned_on_time: bool) -> tuple[int, int, int]:
    """Return (first_night, additional, delay) in pence."""
    first_night_p = daily_p * qty
    add_per_night = (daily_p * qty * ADDITIONAL_NIGHT_MULTIPLIER_NUM) // ADDITIONAL_NIGHT_MULTIPLIER_DEN
    additional_p = add_per_night * max(0, nights - 1)
    extra_delay_p = 0 if returned_on_time else add_per_night
    return first_night_p, additional_p, extra_delay_p


def read_item_lines(nights: int, returned_on_time: bool) -> list[dict]:
    """Collect item lines, computing totals eagerly for downstream reporting."""
    print(ITEM_LINES_INSTRUCTIONS)
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

        try:
            code, qty = _parse_item_line(raw)
        except ValueError as err:
            print(err)
            continue

        item = find_item(code)  # safe after _parse_item_line
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


# ---------------- Task 2 flow: option 1 only ----------------

def run_hire_flow(state: AppState) -> None:
    """Interactively capture hire data and persist it to state (Task 2)."""
    header = read_customer_header()
    if header is None:
        print("Returning to main menu.")
        return

    nights = read_positive_int("Number of nights: ", min_value=1)
    returned_on_time = read_yes_no("Returned on time (y/n)? ")
    lines = read_item_lines(nights, returned_on_time)

    items_summary = ", ".join(f"{ln['name']} – {ln['qty']}" for ln in lines)
    extra_delay_p = sum(ln["extra_delay_p"] for ln in lines)
    total_p = sum(ln["line_total_p"] for ln in lines)

    hire = {
        "customer_id": state.next_customer_id,
        "customer_name": header["customer_name"],
        "nights": nights,
        "returned_on_time": returned_on_time,  # bool internally
        "lines": lines,
        "extra_delay_p": extra_delay_p,
        "total_p": total_p,
        "items_summary": items_summary,
    }
    state.hire_records.append(hire)
    state.next_customer_id += 1

    print("\nSaved hire (Task 2):")
    print(f"  Customer ID: {hire['customer_id']}")
    print(f"  Customer:    {hire['customer_name']}")
    print(f"  Equipment:   {items_summary}")
    print(f"  Nights:      {nights}")
    print(f"  Returned on time: {'y' if returned_on_time else 'n'}")
    print(f"  Extra charge for delayed return: {money(extra_delay_p)}")
    print(f"  Total cost:  {money(total_p)}\n")


# ---------------- Entry point (menu with Task 2 behaviour) ----------------

def main() -> None:
    """Run the main menu loop; Task 2 implements option 1 only."""
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
            print("(Task 3) Report is not implemented in Task 2.")
        elif choice == 3:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()