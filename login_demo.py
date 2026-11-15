
import json
import os
import hashlib
import secrets
from getpass import getpass

USER_FILE = "users.json"

# Demo administrator account
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@123"


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return json.load(file)
    return {}


def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()

    return salt, hashed


def register_citizen():
    users = load_users()

    username = input("Create username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    if username.lower() == ADMIN_USERNAME.lower():
        print("This username is reserved.")
        return

    if username in users:
        print("Username already exists.")
        return

    password = getpass("Create password: ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    salt, hashed = hash_password(password)

    users[username] = {
        "salt": salt,
        "password_hash": hashed,
        "role": "citizen"
    }

    save_users(users)
    print("Citizen registration successful!")


def citizen_login():
    users = load_users()

    username = input("Username: ").strip()
    password = getpass("Password: ")

    user = users.get(username)

    if user is None:
        print("Invalid username or password.")
        return None

    salt, hashed = hash_password(password, user["salt"])

    if secrets.compare_digest(hashed, user["password_hash"]):
        print("Citizen login successful!")
        return username

    print("Invalid username or password.")
    return None


def admin_login():
    username = input("Admin username: ").strip()
    password = getpass("Admin password: ")

    if (
        username == ADMIN_USERNAME
        and secrets.compare_digest(password, ADMIN_PASSWORD)
    ):
        print("Administrator login successful!")
        return True

    print("Invalid administrator credentials.")
    return False


def citizen_menu(username):
    while True:
        print("\n--- CITIZEN MENU ---")
        print("1. Register Complaint")
        print("2. View My Complaints")
        print("3. Check Complaint Status")
        print("4. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            print("Connect your existing complaint registration function here.")

        elif choice == "2":
            print("Connect your own complaints viewing function here.")

        elif choice == "3":
            print("Connect your complaint status function here.")

        elif choice == "4":
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice.")


def admin_menu():
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. View All Complaints")
        print("2. Update Complaint Status")
        print("3. Escalate Pending Complaints")
        print("4. View Statistics")
        print("5. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            print("Connect your existing view complaints function.")

        elif choice == "2":
            print("Connect your existing update status function.")

        elif choice == "3":
            print("Connect your existing escalation function.")

        elif choice == "4":
            print("Connect your existing statistics function.")

        elif choice == "5":
            print("Admin logged out.")
            break

        else:
            print("Invalid choice.")


def main():
    while True:
        print("\n===== CIVICCONNECT =====")
        print("1. Citizen Registration")
        print("2. Citizen Login")
        print("3. Administrator Login")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register_citizen()

        elif choice == "2":
            username = citizen_login()

            if username:
                citizen_menu(username)

        elif choice == "3":
            if admin_login():
                admin_menu()

        elif choice == "4":
            print("Thank you for using CivicConnect!")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
