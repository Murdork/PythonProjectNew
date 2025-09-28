# ==========================================
# Aim to simplify and reduce complexity
# AUDIENCE - shop staff
# ER
# Availalable eq list>? 
# tip?
# Example-check valid?

# ER report skewqered
# trailing spaces before 2nd line
# REFER TO BRIEF to check ER output
# give table fixed width? Take left (width)

# COM4018 – Introduction to Programming
# Task 3B + prerequisites (Tasks 1–3 integrated)
# One-file console app — no imports required.
#
# Pricing rules implemented from the brief:
# • First night = 100% of listed daily rate.
# • Each additional night = +50% of the daily rate (per item, per night).
# • If returned after 2pm, charge one extra “additional night” (+50%) per item.
# • Catalogue and prices follow Figure 2 (Tackle hire list).  【7:Introduction to Programming - COM4018 - [4526].pdf†Source.file†L37-L66】
# • Scenario text with the 2pm rule and discount wording.  【7:Introduction to Programming - COM4018 - [4526].pdf†Source.file†L9-L21】
#
# Money is handled in integer pence to avoid float errors.
# ==========================================

# -----------------------------
# Read-only equipment catalogue (Figure 2)
# -----------------------------
CATALOG = (
    {"code": "DCH", "name": "Day chairs",                           "daily_p": 1500},  # £15.00
    {"code": "BCH", "name": "Bed chairs",                           "daily_p": 2500},  # £25.00
    {"code": "BAS", "name": "Bite Alarm (set of 3)",                "daily_p": 2000},  # £20.00
    {"code": "BA1", "name": "Bite Alarm (single)",                  "daily_p":  500},  # £5.00
    {"code": "BBT", "name": "Bait Boat",                            "daily_p": 6000},  # £60.00
    {"code": "TNT", "name": "Camping tent",                         "daily_p": 2000},  # £20.00
    {"code": "SLP", "name": "Sleeping bag",                         "daily_p": 2000},  # £20.00
    {"code": "R3T", "name": "Rods (3lb TC)",                        "daily_p": 1000},  # £10.00
    {"code": "RBR", "name": "Rods (Bait runners)",                  "daily_p":  500},  # £5.00
    {"code": "REB", "name": "Reels (Bait runners)",                 "daily_p": 1000},  # £10.00
    {"code": "STV", "name": "Camping Gas stove (Double burner)",    "daily_p": 1000},  # £10.00
)

# -----------------------------
# Mutable store (lives only for this run)
# -----------------------------
HIRE_RECORDS = []        # list of hire dicts (each hire has 1+ item lines)
_next_customer_id = 101  # simple running ID (matches brief screenshots style) 【7:Introduction to Programming - COM4018 - [4526].pdf†Source.file†L104-L114】

# -----------------------------
# Utilities (no imports)
# -----------------------------
def money(pence):
    """Format integer pence as £x,xxx.xx (no thousands sep needed in brief, but safe)."""
    pounds = pence // 100
    pp = pence % 100
    return f"£{pounds}.{pp:02d}"

def show_catalog():
    """Print the read-only equipment list."""
    print("\nAvailable equipment (read-only)")
    print("CODE  ITEM                                        RATE/NIGHT")
    print("----  ------------------------------------------  ----------")
    for it in CATALOG:
        print(f"{it['code']:<4}  {it['name']:<42}  {money(it['daily_p']):>10}")

def find_item(code):
    """Return the catalog dict for a code, or None."""
    code = code.strip().upper()
    for item in CATALOG:
        if item["code"] == code:
            return item
    return None

def catalog_codes():
    """Return a comma-separated list of known codes."""
    return ", ".join([it["code"] for it in CATALOG])

def display_menu():
    """Main menu UI (Task 1)."""
    print("\n=== Main Menu ===")
    print("1) Customer & hire details")
    print("2) Earnings report")
    print("3) Exit")

def read_choice():
    """Read a menu choice (1–3). Return int or None if invalid."""
    s = input("Select an option (1-3): ").strip()
    if not s.isdigit():
        return None
    n = int(s)
    return n if n in (1, 2, 3) else None

def read_yes_no(prompt="(y/n): "):
    """Read 'y' or 'n' (accepts 'yes'/'no'). Returns 'y' or 'n'."""
    while True:
        s = input(prompt).strip().lower()
        if s in ("y", "n", "yes", "no"):
            return "y" if s.startswith("y") else "n"
        print("Please enter 'y' or 'n'.")

def parse_csv_line(line):
    """
    Basic CSV parser supporting quotes and commas (no imports).
    Returns list of fields with surrounding spaces trimmed.
    """
    fields = []
    buf = []
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        if in_quotes:
            if ch == '"':
                # doubled quote -> literal "
                if i + 1 < len(line) and line[i+1] == '"':
                    buf.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                buf.append(ch)
        else:
            if ch == '"':
                in_quotes = True
            elif ch == ',':
                fields.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
        i += 1
    fields.append("".join(buf).strip())
    return fields

# -----------------------------
# Input: Customer + Hire header (Task 2)
# -----------------------------
def read_customer_header():
    """
    Prompt for customer & hire header on one line (comma/quoted):
      name, phone, house_no, postcode, card_last4
    Minimal validation: non-empty name; phone ≥7 digits; card_last4 exactly 4 digits.
    Returns dict or None if user cancels.
    """
    print("\nEnter customer details (one line, comma/quoted separated):")
    print("  name, phone, house_no, postcode, card_last4")
    print("  Example: Bob Barker,07970263076,3b,WA9 RY,1452")
    while True:
        raw = input("> ").strip()
        if raw == "":
            if read_yes_no("No details entered. Return to main menu (y/n)? ") == "y":
                return None
            else:
                continue

        parts = parse_csv_line(raw)
        if len(parts) != 5:
            print("Expected 5 fields. Try again.")
            continue

        name, phone, house_no, postcode, card_last4 = [p.strip() for p in parts]
        digits_phone = "".join(ch for ch in phone if ch.isdigit())
        digits_card  = "".join(ch for ch in card_last4 if ch.isdigit())

        if not name:
            print("Name cannot be empty.")
            continue
        if len(digits_phone) < 7:
            print("Phone must have at least 7 digits.")
            continue
        if len(digits_card) != 4:
            print("Card last 4 must be exactly 4 digits.")
            continue

        return {
            "customer_name": name,
            "phone": digits_phone,
            "house_no": house_no,
            "postcode": postcode,
            "card_last4": digits_card,
        }

def read_positive_int(prompt, min_value=1):
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

def read_item_lines(nights, returned_on_time):
    """
    Enter item lines for this hire.
    Format per line (comma/quoted): CODE, quantity
    Blank line finishes.
    Returns list of computed line dicts.
    """
    print("\nEnter item lines (one per line), then press ENTER on a blank line to finish.")
    print("Format: CODE, quantity   e.g.,  DCH, 2")
    print(f"Nights for this hire: {nights}  | Returned on time: {returned_on_time}")
    print(f"Known codes: {catalog_codes()}")
    lines = []
    while True:
        raw = input("> ").strip()
        if raw == "":
            if len(lines) == 0:
                print("You must enter at least one item.")
                continue
            break
        parts = [p.strip() for p in parse_csv_line(raw)]
        if len(parts) != 2:
            print("Expected 2 fields: CODE, quantity")
            continue
        code = parts[0].upper()
        item = find_item(code)
        if not item:
            print(f"Unknown code '{code}'. Known: {catalog_codes()}")
            continue
        if not parts[1].isdigit():
            print("Quantity must be a whole number.")
            continue
        qty = int(parts[1])
        if qty < 1:
            print("Quantity must be ≥ 1.")
            continue

        # Compute costs using Task 3 pricing rules
        daily = item["daily_p"]
        # First night full price per item
        first_night_p = daily * qty
        # Additional nights charged at 50% per night, per item
        additional_n = max(0, nights - 1)
        additional_p  = (daily * qty * additional_n) // 2
        # Late return (after 2pm) = one extra “additional night” (+50%) per item
        late_extra_p  = 0 if returned_on_time == "y" else (daily * qty) // 2

        line_total_p = first_night_p + additional_p + late_extra_p

        lines.append({
            "code": item["code"],
            "name": item["name"],
            "daily_p": daily,
            "qty": qty,
            "first_night_p": first_night_p,
            "additional_n": additional_n,
            "additional_p": additional_p,
            "late_extra_p": late_extra_p,
            "line_total_p": line_total_p,
        })
    return lines

# -----------------------------
# Task 2 — Hire workflow
# -----------------------------
def run_hire_flow():
    """
    Option 1: capture hires repeatedly (customer -> nights -> on-time? -> items).
    """
    global _next_customer_id

    show_catalog()
    print("\nTip: Press Enter at the first prompt to return to the main menu.\n")

    while True:
        header = read_customer_header()
        if header is None:
            print("Returning to main menu.")
            return

        nights = read_positive_int("Number of nights (≥1): ", 1)
        returned_on_time = read_yes_no("Returned on time (y/n)? ")

        lines = read_item_lines(nights, returned_on_time)

        # Compute hire totals
        total_p = 0
        extra_delay_p = 0
        for ln in lines:
            total_p += ln["line_total_p"]
            extra_delay_p += ln["late_extra_p"]

        # Save the hire
        hire = {
            "customer_id": _next_customer_id,
            "customer_name": header["customer_name"],
            "phone": header["phone"],
            "house_no": header["house_no"],
            "postcode": header["postcode"],
            "card_last4": header["card_last4"],
            "nights": nights,
            "returned_on_time": returned_on_time,
            "extra_delay_p": extra_delay_p,   # column in Figure 4
            "total_p": total_p,               # total hire cost
            "lines": lines,
        }
        HIRE_RECORDS.append(hire)
        _next_customer_id += 1

        # Show a brief confirmation (like Figure 3/4 combined)
        items_summary = ", ".join([f"{ln['name']} – {ln['qty']}" for ln in lines])
        print("\nSaved hire:")
        print(f"  Customer ID: {hire['customer_id']}")
        print(f"  Equipment:   {items_summary}")
        print(f"  Nights:      {nights}")
        print(f"  Returned on time: {returned_on_time}")
        print(f"  Extra charge for delayed return: {money(extra_delay_p)}")
        print(f"  Total cost:  {money(total_p)}\n")

        if read_yes_no("Add another hire (y/n)? ") == "n":
            print("Returning to main menu.")
            return

# -----------------------------
# Task 3B — Earnings report
def run_earnings_report():
    """
    Produce an earnings report similar to Figure 4:
    Columns: Customer ID | Equipment | Number of nights | Total Cost | Returned on time (y/n) | Extra charge for delayed return
    Also prints a summary footer with TOTAL EARNINGS.
    """
    if not HIRE_RECORDS:
        print("\nNo hires recorded yet.")
        return

    print("\n" + "-"*120)
    print("Earnings Report")
    print("-" * 120)
    # Print header
    header = (
        f"{'ID':<4} | {'Customer Name':<20} | {'Equipment (Name – Qty)':<45} | "
        f"{'Nights':>6} | {'On-Time':>7} | {'Late Fee':>10} | {'Total Cost':>12}"
    )
    print(header)
    print("-" * 120)

    grand_total = 0
    for r in HIRE_RECORDS:
        items_summary = ", ".join([f"{ln['name']} – {ln['qty']}" for ln in r["lines"]])
        # Truncate long summaries to fit the column
        if len(items_summary) > 42:
            items_summary = items_summary[:39] + "..."
        
        # Print a single row for the record
        row = (
            f"{r['customer_id']:<4} | {r['customer_name']:<20} | {items_summary:<45} | "
            f"{r['nights']:>6} | {r['returned_on_time']:>7} | {money(r['extra_delay_p']):>10} | {money(r['total_p']):>12}"
        )
        print(row)
        grand_total += r["total_p"]

    print("-" * 120)
    print(f"TOTAL EARNINGS: {money(grand_total):>107}")
    print("-" * 120)
    
# -----------------------------
# Main loop (Task 1 driver)
# -----------------------------
def main():
    while True:
        display_menu()
        choice = read_choice()
        if choice is None:
            print("Invalid option, try again.")
            continue

        if choice == 1:
            run_hire_flow()
        elif choice == 2:
            run_earnings_report()
        elif choice == 3:
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()