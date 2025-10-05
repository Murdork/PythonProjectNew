"""COM4018 – Equipment Hire Console App (Tasks 2 & 3)

A menu-driven console programme for a small shop that hires fishing and camping equipment.

Design notes:
- Money is stored as integer pence to avoid floating-point rounding issues.
- Pricing rules: first night at 100%; each additional night at 50%; late returns incur one extra 50% night.
- Reference data (catalogue) is read-only and separate from mutable state.
- Input parsing is split into pure functions (raise on error) and interactive readers (loop with messages).
- Documentation follows PEP 257 docstrings. No imports are used.
"""

# ---------- User-facing instructional text ----------

CUSTOMER_ENTRY_INSTRUCTIONS = (
    "\nEnter customer (comma separated):\n"
    "  customer_id, name, phone, house_no, postcode, card_last4\n"
    "  Example:  101, Jane Smith, 07900111222, 12, LE1 2AB, 1234"
)

ITEM_LINES_INSTRUCTIONS = (
    "\nEnter item lines (one per line), then press ENTER on a blank line to finish.\n"
    "Format: CODE, quantity   e.g.,  DCH, 2"
)

MAIN_MENU_LINES = (
    "\n=== Main Menu ===",
    "1) Enter details of customer and equipment hired",
    "2) Create report",
    "3) Exit",
)

PROMPT_SELECT_OPTION = "Select an option (1-3): "

# ---------- Catalogue (code → (name, daily_pence)) ----------

CATALOG = {
    "DCH": ("Day chairs", 1500),
    "BCH": ("Bed chairs", 2500),
    "BAS": ("Bite Alarm (set of 3)", 2000),
    "BA1": ("Bite Alarm (single)", 500),
    "BBT": ("Bait Boat", 6000),
    "TNT": ("Camping tent", 2000),
    "SLP": ("Sleeping bag", 2000),
    "R3T": ("Rods (3lb TC)", 1000),
    "RBR": ("Rods (Bait runners)", 500),
    "REB": ("Reels (Bait runners)", 1000),
    "STV": ("Camping Gas stove (Double burner)", 1000),
}

# Pricing multiplier for additional nights (50%)
ADDITIONAL_NIGHT_MULTIPLIER_NUM = 1
ADDITIONAL_NIGHT_MULTIPLIER_DEN = 2

# ---------- State ----------

class AppState:
    """Holds mutable programme state for the current run."""
    def __init__(self) -> None:
        self.hire_records: list[dict] = []

# ---------- Utilities ----------

def money(pence: int) -> str:
    """Return integer pence as a sterling string '£x.xx'."""
    pounds, pennies = pence // 100, pence % 100
    return f"£{pounds}.{pennies:02d}"

def catalog_codes() -> str:
    """Return a comma-separated catalogue code summary for prompts."""
    return ", ".join(CATALOG.keys())

def print_main_menu() -> None:
    """Display the main menu exactly as specified in the brief."""
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
        if s in ("y", "yes"): return True
        if s in ("n", "no"):  return False
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

# ---------- Pure parsers ----------

def _parse_customer_header(raw: str) -> dict:
    """Parse customer CSV: 'customer_id, name, phone, house_no, postcode, card_last4'.

    Raises:
        ValueError: If the expected fields are missing or invalid.
    """
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 6:
        raise ValueError("Expected 6 fields separated by commas.")
    id_s, name, phone, house_no, postcode, card_last4 = parts

    try:
        customer_id = int(id_s)
    except ValueError as exc:
        raise ValueError("Customer ID must be a whole number.") from exc
    if customer_id <= 0:
        raise ValueError("Customer ID must be ≥ 1.")
    if not name:
        raise ValueError("Name cannot be empty.")

    phone_digits = "".join(ch for ch in phone if ch.isdigit())
    if len(phone_digits) < 7:
        raise ValueError("Phone should contain at least 7 digits.")

    card_digits = "".join(ch for ch in card_last4 if ch.isdigit())
    if len(card_digits) != 4:
        raise ValueError("Card last 4 digits must be exactly 4 digits.")

    return {
        "customer_id": customer_id,
        "customer_name": name,
        "phone": phone_digits,
        "house_no": house_no,
        "postcode": postcode.upper(),
        "card_last4": card_digits,
    }

def _parse_item_line(raw: str) -> tuple[str, int]:
    """Return (code, qty) parsed from raw, or raise ValueError."""
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 2:
        raise ValueError("Expected 2 fields: CODE, quantity")

    code, qty_s = parts[0].upper(), parts[1]
    if code not in CATALOG:
        raise ValueError(f"Unknown code '{code}'. Known: {catalog_codes()}")
    try:
        qty = int(qty_s)
    except ValueError as exc:
        raise ValueError("Quantity must be a whole number.") from exc
    if qty < 1:
        raise ValueError("Quantity must be ≥ 1.")
    return code, qty

# ---------- Interactive readers ----------

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

def calc_line_costs(daily_p: int, qty: int, nights: int, on_time: bool) -> tuple[int, int, int]:
    """Return (first_night_p, additional_nights_p, extra_delay_p) in pence."""
    first = daily_p * qty
    # Using rational multiplier for clarity: (qty*daily) * 1/2 per extra night
    add_each = (daily_p * qty * ADDITIONAL_NIGHT_MULTIPLIER_NUM) // ADDITIONAL_NIGHT_MULTIPLIER_DEN
    additional = add_each * max(0, nights - 1)
    extra = 0 if on_time else add_each
    return first, additional, extra

def read_item_lines(nights: int, on_time: bool) -> list[dict]:
    """Collect item lines, computing totals eagerly for downstream reporting."""
    print(ITEM_LINES_INSTRUCTIONS)
    print(f"Nights for this hire: {nights}  | Returned on time: {on_time}")
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

        name, daily = CATALOG[code]
        first_p, add_p, delay_p = calc_line_costs(daily, qty, nights, on_time)
        lines.append({
            "code": code,
            "name": name,
            "qty": qty,
            "daily_p": daily,
            "first_night_p": first_p,
            "additional_nights_p": add_p,
            "extra_delay_p": delay_p,
            "line_total_p": first_p + add_p + delay_p,
        })

# ---------- Reporting helpers (word-wrapped Equipment column) ----------

def _wrap_equipment(text: str, width: int) -> list[str]:
    """Word-wrap a comma-separated equipment string to a fixed width."""
    lines: list[str] = []
    cur = ""

    def flush() -> None:
        nonlocal cur
        if cur:
            lines.append(cur.ljust(width))
            cur = ""

    for item in (p.strip() for p in text.split(",") if p.strip()):
        if len(item) > width:
            flush()
            for i in range(0, len(item), width):
                chunk = item[i:i + width]
                lines.append(chunk if len(chunk) == width else chunk.ljust(width))
            continue

        token = (", " if cur else "") + item
        if len(cur) + len(token) <= width:
            cur += token
        else:
            flush()
            cur = item

    if cur or not lines:
        lines.append(cur.ljust(width))
    return lines

# ---------- Flows ----------

def run_hire_flow(state: AppState) -> None:
    """Interactively capture hire data and persist it to state."""
    while True:
        header = read_customer_header()
        if header is None:
            print("Returning to main menu.")
            return

        nights = read_positive_int("Number of nights: ", min_value=1)
        on_time = read_yes_no("Returned on time (y/n)? ")
        lines = read_item_lines(nights, on_time)

        items_summary = ", ".join(f"{ln['name']} – {ln['qty']}" for ln in lines)
        extra_delay_p = sum(ln["extra_delay_p"] for ln in lines)
        total_p = sum(ln["line_total_p"] for ln in lines)

        hire = {
            "customer_id": header["customer_id"],      # manually entered now
            "customer_name": header["customer_name"],
            "nights": nights,
            "returned_on_time": on_time,
            "lines": lines,
            "extra_delay_p": extra_delay_p,
            "total_p": total_p,
            "items_summary": items_summary,
        }
        state.hire_records.append(hire)

        print("\nSaved hire:")
        print(f"  Customer ID: {hire['customer_id']}")
        print(f"  Customer:    {hire['customer_name']}")
        print(f"  Equipment:   {items_summary}")
        print(f"  Nights:      {nights}")
        print(f"  Returned on time: {'y' if on_time else 'n'}")
        print(f"  Extra charge for delayed return: {money(extra_delay_p)}")
        print(f"  Total cost:  {money(total_p)}\n")

        if not read_yes_no("Add another hire (y/n)? "):
            print("Returning to main menu.")
            return

def run_earnings_report(state: AppState) -> None:
    """Print a fixed-width earnings table with word-wrapped Equipment.

    Columns:
        Customer ID | Equipment | Number of nights | Total Cost | Returned on time (y/n) | Extra charge for delayed return

    Notes:
        - Monetary columns show pounds and pence (e.g., £157.00).
        - Equipment wraps onto continuation rows; other columns are blank on wrapped rows.
    """
    if not state.hire_records:
        print("\nNo hires recorded yet.")
        return

    # Column widths (must match header ruler below)
    ID_W, EQUIP_W, NIGHTS_W, TOTAL_W, ONTIME_W, EXTRA_W = 11, 65, 16, 10, 22, 30

    # Headers (verbatim layout from brief)
    print("Customer ID | Equipment                                                       | Number of nights | Total Cost | Returned on time (y/n) | Extra charge for delayed return")
    print("------------+-----------------------------------------------------------------+------------------+------------+------------------------+--------------------------------")

    for h in state.hire_records:
        total_money = money(h["total_p"])
        extra_money = money(h["extra_delay_p"])
        on_time_char = "y" if h["returned_on_time"] else "n"
        lines = _wrap_equipment(h["items_summary"], EQUIP_W)

        # First row carries all fields
        print(
            f"{h['customer_id']:<{ID_W}} | "
            f"{lines[0]} | "
            f"{h['nights']:<{NIGHTS_W}} | "
            f"{total_money:<{TOTAL_W}} | "
            f"{on_time_char:<{ONTIME_W}} | "
            f"{extra_money:<{EXTRA_W}}"
        )
        # Continuation rows: only Equipment is populated
        for cont in lines[1:]:
            print(
                f"{'':<{ID_W}} | "
                f"{cont} | "
                f"{'':<{NIGHTS_W}} | "
                f"{'':<{TOTAL_W}} | "
                f"{'':<{ONTIME_W}} | "
                f"{'':<{EXTRA_W}}"
            )

# ---------- Entry point ----------

def main() -> None:
    """Run the main menu loop until the user chooses to exit."""
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
