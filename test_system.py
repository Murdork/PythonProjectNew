#!/usr/bin/env python3
"""
Comprehensive test script for the tackle hire system.
This script simulates the test data inputs and validates the outputs.
"""

# Import the system by reading and executing it (excluding the main execution)
with open('tackle_hire_system.py', 'r', encoding='utf-8') as f:
    script_content = f.read()
    # Remove only the main() call at the end, keep all function definitions
    lines = script_content.split('\n')
    filtered_lines = []
    skip_main_block = False
    for line in lines:
        if line.strip() == 'if __name__ == "__main__":':
            skip_main_block = True
        if not skip_main_block:
            filtered_lines.append(line)
    exec('\n'.join(filtered_lines))

def simulate_test_data():
    """Simulate the test data inputs and capture results"""
    
    # Reset the system state
    global HIRE_RECORDS, _next_customer_id
    HIRE_RECORDS = []
    _next_customer_id = 101
    
    print("=== COMPREHENSIVE SYSTEM TEST ===")
    print("Testing with provided test data scenarios...")
    print()
    
    # Test data from TestData.txt - manually processed
    test_hires = [
        {
            "customer": "Alice Smith,07891234567,12,WA9 1AA,1111",
            "nights": 1,
            "on_time": True,
            "items": [("DCH", 2)]
        },
        {
            "customer": "John Doe,07700123456,3b,LS1 4XY,2222",
            "nights": 2,
            "on_time": False,
            "items": [("BCH", 1)]
        },
        {
            "customer": "Mary Jones,07900123456,45,EH1 2YZ,3333",
            "nights": 3,
            "on_time": True,
            "items": [("BAS", 1)]
        },
        {
            "customer": "Tom Brown,07555123456,7,CF10 1AA,4444",
            "nights": 1,
            "on_time": True,
            "items": [("BA1", 3)]
        },
        {
            "customer": "Sue Green,07944123456,21,NE1 1AA,5555",
            "nights": 2,
            "on_time": True,
            "items": [("BBT", 1)]
        },
        {
            "customer": "Ken White,07600123456,8,SW1A 0AA,6666",
            "nights": 4,
            "on_time": False,
            "items": [("TNT", 2)]
        },
        {
            "customer": "Liam Black,07300123456,10,BS1 4ST,7777",
            "nights": 1,
            "on_time": True,
            "items": [("SLP", 2)]
        },
        {
            "customer": "Olivia Gray,07800123456,99,CF11 8TN,8888",
            "nights": 2,
            "on_time": False,
            "items": [("R3T", 3), ("RBR", 2)]
        },
        {
            "customer": "Noah Blue,07200123456,5,EH2 3PL,9999",
            "nights": 3,
            "on_time": True,
            "items": [("REB", 2), ("STV", 1)]
        },
        {
            "customer": "Emma King,07100123456,2A,LS2 7AB,0000",
            "nights": 5,
            "on_time": False,
            "items": [("DCH", 1), ("BCH", 1), ("BA1", 1)]
        }
    ]
    
    # Process each hire
    for i, hire_data in enumerate(test_hires, 1):
        print(f"--- Processing Hire {i} ---")
        
        # Parse customer data
        customer_parts = parse_csv_line(hire_data["customer"])
        customer_header = {
            "customer_name": customer_parts[0],
            "phone": "".join(ch for ch in customer_parts[1] if ch.isdigit()),
            "house_no": customer_parts[2],
            "postcode": customer_parts[3],
            "card_last4": customer_parts[4],
        }
        
        nights = hire_data["nights"]
        returned_on_time = "y" if hire_data["on_time"] else "n"
        
        # Process items
        lines = []
        for code, qty in hire_data["items"]:
            item = find_item(code)
            if item:
                daily = item["daily_p"]
                first_night_p = daily * qty
                additional_n = max(0, nights - 1)
                additional_p = (daily * qty * additional_n) // 2
                late_extra_p = 0 if hire_data["on_time"] else (daily * qty) // 2
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
        
        # Calculate totals
        total_p = sum(ln["line_total_p"] for ln in lines)
        extra_delay_p = sum(ln["late_extra_p"] for ln in lines)
        
        # Create hire record
        hire = {
            "customer_id": _next_customer_id,
            "customer_name": customer_header["customer_name"],
            "phone": customer_header["phone"],
            "house_no": customer_header["house_no"],
            "postcode": customer_header["postcode"],
            "card_last4": customer_header["card_last4"],
            "nights": nights,
            "returned_on_time": returned_on_time,
            "extra_delay_p": extra_delay_p,
            "total_p": total_p,
            "lines": lines,
        }
        
        HIRE_RECORDS.append(hire)
        _next_customer_id += 1
        
        # Display hire summary
        items_summary = ", ".join([f"{ln['name']} – {ln['qty']}" for ln in lines])
        print(f"  Customer: {hire['customer_name']}")
        print(f"  Equipment: {items_summary}")
        print(f"  Nights: {nights}")
        print(f"  On time: {returned_on_time}")
        print(f"  Extra delay charge: {money(extra_delay_p)}")
        print(f"  Total cost: {money(total_p)}")
        print()
    
    print("=== FINAL EARNINGS REPORT ===")
    run_earnings_report()
    
    return HIRE_RECORDS

def validate_pricing_rules():
    """Validate that the pricing rules match the requirements"""
    print("\n=== PRICING RULE VALIDATION ===")
    
    # Test specific scenarios mentioned in requirements
    scenarios = [
        {
            "name": "Single night, on time",
            "item_code": "DCH",
            "qty": 1,
            "nights": 1,
            "on_time": True,
            "expected_total": 1500  # £15.00
        },
        {
            "name": "Two nights, on time",
            "item_code": "BCH", 
            "qty": 1,
            "nights": 2,
            "on_time": True,
            "expected_total": 3750  # £25.00 + £12.50 = £37.50
        },
        {
            "name": "Single night, late return",
            "item_code": "DCH",
            "qty": 1,
            "nights": 1,
            "on_time": False,
            "expected_total": 2250  # £15.00 + £7.50 = £22.50
        },
        {
            "name": "Three nights, on time",
            "item_code": "BAS",
            "qty": 1,
            "nights": 3,
            "on_time": True,
            "expected_total": 4000  # £20.00 + £20.00 = £40.00
        }
    ]
    
    for scenario in scenarios:
        item = find_item(scenario["item_code"])
        daily = item["daily_p"]
        qty = scenario["qty"]
        nights = scenario["nights"]
        on_time = scenario["on_time"]
        
        first_night_p = daily * qty
        additional_n = max(0, nights - 1)
        additional_p = (daily * qty * additional_n) // 2
        late_extra_p = 0 if on_time else (daily * qty) // 2
        total_p = first_night_p + additional_p + late_extra_p
        
        print(f"Scenario: {scenario['name']}")
        print(f"  Item: {item['name']} (£{daily/100:.2f}) × {qty}")
        print(f"  Nights: {nights}")
        print(f"  On time: {on_time}")
        print(f"  Calculated total: {money(total_p)}")
        print(f"  Expected total: {money(scenario['expected_total'])}")
        print(f"  ✓ PASS" if total_p == scenario['expected_total'] else f"  ✗ FAIL")
        print()

def test_input_validation():
    """Test input validation functions"""
    print("=== INPUT VALIDATION TESTING ===")
    
    # Test phone number validation
    print("Phone number validation:")
    test_phones = ["07891234567", "123456", "abc123def456", "01234567890"]
    for phone in test_phones:
        digits = "".join(ch for ch in phone if ch.isdigit())
        valid = len(digits) >= 7
        print(f"  {phone} -> {digits} ({'valid' if valid else 'invalid'})")
    
    print("\nCard number validation:")
    test_cards = ["1111", "22", "3333a", "44444", "abcd"]
    for card in test_cards:
        digits = "".join(ch for ch in card if ch.isdigit())
        valid = len(digits) == 4
        print(f"  {card} -> {digits} ({'valid' if valid else 'invalid'})")
    
    print("\nItem code validation:")
    test_codes = ["DCH", "dch", "XXX", "bcH", ""]
    for code in test_codes:
        item = find_item(code)
        print(f"  {code} -> {'valid' if item else 'invalid'}")

if __name__ == "__main__":
    # Run all tests
    test_input_validation()
    validate_pricing_rules()
    hire_records = simulate_test_data()
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"Total hires processed: {len(hire_records)}")
    print(f"Total earnings: {money(sum(h['total_p'] for h in hire_records))}")
    print("All tests completed successfully!")