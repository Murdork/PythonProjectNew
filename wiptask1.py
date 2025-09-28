def display_menu():
    """Displays the main menu."""
    print("\n--- Main Menu ---")
    print("1. Customer and hire details")
    print("2. Earnings report")
    print("3. Exit")

def main():
    """Main function to run the program."""
    while True:
        display_menu()
        choice = input("Please select an option (1-3): ")

        if choice == '1':
            print("\nCustomer and hire details selected")
        elif choice == '2':
            print("\nEarnings report selected")
        elif choice == '3':
            print("\nExiting the program. Goodbye!")
            break
        else:
            print("\nInvalid input. Please enter a number between 1 and 3.")

if __name__ == "__main__":
    main()
