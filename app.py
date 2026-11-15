# ============================================================
# CivicConnect - Complaint Routing and Escalation System
# CP-073 | Python Console Application
# ============================================================

import os
import json
import hashlib
import secrets
import hmac
from getpass import getpass
from datetime import date, datetime

# -------------------- CONSOLE COLORS --------------------
RESET = "\033[0m"
BOLD = "\033[1m"
BG_BLACK = "\033[48;2;34;34;34m"
MAUVE = "\033[38;2;155;133;143m"
BEIGE = "\033[38;2;232;221;210m"
GREEN = "\033[92m"
RED = "\033[91m"
HIGHLIGHT = "\033[48;2;155;133;143m"
HIGHLIGHT_TEXT = "\033[38;2;34;34;34m"

# -------------------- SETTINGS --------------------
DATA_FILE = "complaints.txt"
USER_FILE = "users.json"
ESCALATION_DAYS = 7

# Demo administrator credentials.
# Change these before using the application beyond a classroom demo.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@123"

CATEGORIES = {
    "1": ("Pothole", "Roads Department"),
    "2": ("Garbage", "Sanitation Department"),
    "3": ("Street Light", "Electrical Department"),
    "4": ("Water Supply", "Water Department"),
    "5": ("Other", "Municipal Department"),
}
STATUSES = ["Received", "Assigned", "In Progress", "Resolved"]

complaints = []
next_id = 1


# -------------------- DISPLAY HELPERS --------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def heading(title):
    print(BG_BLACK + MAUVE + BOLD)
    print("=" * 60)
    print(title.center(60))
    print("=" * 60 + RESET)


def success(message):
    print(BG_BLACK + GREEN + BOLD + "\n✓ " + message + RESET)


def error(message):
    print(BG_BLACK + RED + BOLD + "\n✗ " + message + RESET)


def normal(message):
    print(BG_BLACK + BEIGE + message + RESET)


def pause():
    input(BG_BLACK + BEIGE + "\nPress Enter to continue..." + RESET)


def menu_option(number, text, highlighted=False):
    if highlighted:
        print(BG_BLACK + HIGHLIGHT + HIGHLIGHT_TEXT + BOLD
              + f" {number}. {text} " + RESET)
    else:
        normal(f" {number}. {text}")


# -------------------- AUTHENTICATION --------------------
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            users = json.load(file)
        return users if isinstance(users, dict) else {}
    except (OSError, json.JSONDecodeError):
        error("Could not read users file.")
        return {}


def save_users(users):
    try:
        with open(USER_FILE, "w", encoding="utf-8") as file:
            json.dump(users, file, indent=4)
    except OSError:
        error("Could not save users.")


def make_password_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000
    ).hex()


def register_citizen():
    heading("CITIZEN REGISTRATION")
    users = load_users()

    username = input(BG_BLACK + BEIGE + "Create username: " + RESET).strip()
    if not username:
        error("Username cannot be empty.")
        return
    if username.lower() == ADMIN_USERNAME.lower():
        error("This username is reserved.")
        return
    if username in users:
        error("Username already exists.")
        return

    password = getpass("Create password (minimum 8 characters): ")
    if len(password) < 8:
        error("Password must contain at least 8 characters.")
        return
    confirm_password = getpass("Confirm password: ")
    if password != confirm_password:
        error("Passwords do not match.")
        return

    salt = secrets.token_hex(16)
    users[username] = {
        "salt": salt,
        "password_hash": make_password_hash(password, salt),
        "role": "citizen"
    }
    save_users(users)
    success("Citizen registration completed!")


def citizen_login():
    heading("CITIZEN LOGIN")
    users = load_users()
    username = input(BG_BLACK + BEIGE + "Username: " + RESET).strip()
    password = getpass("Password: ")

    user = users.get(username)
    if user and user.get("role") == "citizen":
        entered_hash = make_password_hash(password, user["salt"])
        if hmac.compare_digest(entered_hash, user["password_hash"]):
            success("Login successful!")
            return username

    error("Invalid username or password.")
    return None


def administrator_login():
    heading("ADMINISTRATOR LOGIN")
    username = input(BG_BLACK + BEIGE + "Admin username: " + RESET).strip()
    password = getpass("Admin password: ")

    if (hmac.compare_digest(username, ADMIN_USERNAME)
            and hmac.compare_digest(password, ADMIN_PASSWORD)):
        success("Administrator login successful!")
        return True

    error("Invalid administrator credentials.")
    return False


# -------------------- DATA HANDLING --------------------
def load_complaints():
    global complaints, next_id
    complaints = []
    next_id = 1

    if not os.path.exists(DATA_FILE):
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.rstrip("\n").split("|")
                try:
                    # Supports old 9-field records and new 10-field records.
                    if len(parts) == 9:
                        owner = "legacy"
                    elif len(parts) == 10:
                        owner = parts[9]
                    else:
                        continue

                    complaint = {
                        "id": int(parts[0]),
                        "category": parts[1],
                        "ward": int(parts[2]),
                        "description": parts[3],
                        "department": parts[4],
                        "status": parts[5],
                        "created": parts[6],
                        "updated": parts[7],
                        "escalated": parts[8] == "True",
                        "owner": owner,
                    }
                    complaints.append(complaint)
                except (ValueError, IndexError):
                    continue

        if complaints:
            next_id = max(c["id"] for c in complaints) + 1
    except OSError:
        error("Could not read complaints file.")


def save_complaints():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            for c in complaints:
                description = c["description"].replace("|", "/").replace("\n", " ")
                owner = c.get("owner", "legacy").replace("|", "/")
                line = (
                    f'{c["id"]}|{c["category"]}|{c["ward"]}|{description}|'
                    f'{c["department"]}|{c["status"]}|{c["created"]}|'
                    f'{c["updated"]}|{c["escalated"]}|{owner}\n'
                )
                file.write(line)
    except OSError:
        error("Could not save complaints.")


def find_complaint(complaint_id):
    for complaint in complaints:
        if complaint["id"] == complaint_id:
            return complaint
    return None


# -------------------- FEATURE 1: REGISTER COMPLAINT --------------------
def register_complaint(owner="legacy"):
    heading("REGISTER A COMPLAINT")
    normal("\nChoose complaint category:")
    for key, (category, department) in CATEGORIES.items():
        normal(f" {key}. {category}")

    category_choice = input(BG_BLACK + BEIGE + "\nCategory number: " + RESET).strip()
    if category_choice not in CATEGORIES:
        error("Invalid category.")
        return

    category, department = CATEGORIES[category_choice]
    ward_text = input(BG_BLACK + BEIGE + "Ward number: " + RESET).strip()
    if not ward_text.isdigit() or int(ward_text) <= 0:
        error("Ward must be a positive number.")
        return

    description = input(BG_BLACK + BEIGE + "Describe the issue: " + RESET).strip()
    if not description:
        error("Description cannot be empty.")
        return

    global next_id
    today = date.today().isoformat()
    complaint = {
        "id": next_id,
        "category": category,
        "ward": int(ward_text),
        "description": description,
        "department": department,
        "status": "Received",
        "created": today,
        "updated": today,
        "escalated": False,
        "owner": owner,
    }

    complaints.append(complaint)
    save_complaints()
    success(f"Complaint registered! ID: CC{next_id:03d}")
    normal(f"Assigned department: {department}")
    next_id += 1


# -------------------- VIEW COMPLAINTS --------------------
def display_complaint(c):
    print(BG_BLACK + MAUVE + BOLD + f"\nComplaint ID: CC{c['id']:03d}" + RESET)
    normal(f"Category: {c['category']}")
    normal(f"Ward: {c['ward']}")
    normal(f"Description: {c['description']}")
    normal(f"Department: {c['department']}")
    normal(f"Status: {c['status']}")
    normal(f"Registered: {c['created']}")
    if c.get("owner") not in (None, "", "legacy"):
        normal(f"Citizen: {c['owner']}")
    if c["escalated"]:
        print(BG_BLACK + RED + BOLD + "ESCALATED" + RESET)
    normal("-" * 45)


def view_complaints():
    heading("ALL COMPLAINTS")
    if not complaints:
        normal("No complaints registered yet.")
        return
    for complaint in complaints:
        display_complaint(complaint)


def view_my_complaints(username):
    heading("MY COMPLAINTS")
    own = [c for c in complaints if c.get("owner") == username]
    if not own:
        normal("You have not registered any complaints yet.")
        return
    for complaint in own:
        display_complaint(complaint)


def check_my_status(username):
    heading("CHECK MY COMPLAINT STATUS")
    own = [c for c in complaints if c.get("owner") == username]
    if not own:
        normal("You have not registered any complaints yet.")
        return

    for complaint in own:
        normal(f"CC{complaint['id']:03d} - {complaint['category']} - "
               f"{complaint['status']}")


# -------------------- FEATURE 3: UPDATE STATUS --------------------
def update_status():
    heading("UPDATE COMPLAINT STATUS")
    if not complaints:
        error("No complaints available.")
        return

    id_text = input(BG_BLACK + BEIGE + "Enter complaint ID (number): " + RESET).strip()
    if not id_text.isdigit():
        error("Complaint ID must be a number.")
        return

    complaint = find_complaint(int(id_text))
    if complaint is None:
        error("Complaint not found.")
        return

    display_complaint(complaint)
    normal("\nChoose new status:")
    for i, status in enumerate(STATUSES, start=1):
        normal(f"{i}. {status}")

    choice = input(BG_BLACK + BEIGE + "Status number: " + RESET).strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(STATUSES):
        error("Invalid status choice.")
        return

    new_status = STATUSES[int(choice) - 1]
    complaint["status"] = new_status
    complaint["updated"] = date.today().isoformat()
    if new_status == "Resolved":
        complaint["escalated"] = False

    save_complaints()
    success(f"Complaint CC{complaint['id']:03d} updated to {new_status}.")


# -------------------- FEATURE 4: ESCALATION --------------------
def escalate_complaints():
    heading("ESCALATE PENDING COMPLAINTS")
    today = date.today()
    escalated_count = 0

    for complaint in complaints:
        if complaint["status"] == "Resolved" or complaint["escalated"]:
            continue
        try:
            created_date = datetime.strptime(
                complaint["created"], "%Y-%m-%d"
            ).date()
        except ValueError:
            continue

        pending_days = (today - created_date).days
        if pending_days > ESCALATION_DAYS:
            complaint["escalated"] = True
            escalated_count += 1
            print(BG_BLACK + RED + BOLD
                  + f"CC{complaint['id']:03d} - Ward {complaint['ward']} "
                  + f"- {pending_days} days pending" + RESET)

    if escalated_count:
        save_complaints()
        success(f"{escalated_count} complaint(s) escalated.")
    else:
        success("No complaints currently require escalation.")


# -------------------- FEATURE 5: STATISTICS --------------------
def view_statistics():
    heading("COMPLAINT STATISTICS")
    if not complaints:
        normal("No data available.")
        return

    print(BG_BLACK + MAUVE + BOLD + "\nWARD-WISE STATISTICS" + RESET)
    for ward in sorted(set(c["ward"] for c in complaints)):
        count = sum(1 for c in complaints if c["ward"] == ward)
        resolved = sum(1 for c in complaints
                       if c["ward"] == ward and c["status"] == "Resolved")
        normal(f"Ward {ward}: {count} total, {resolved} resolved")

    print(BG_BLACK + MAUVE + BOLD + "\nDEPARTMENT-WISE STATISTICS" + RESET)
    for department in sorted(set(c["department"] for c in complaints)):
        count = sum(1 for c in complaints if c["department"] == department)
        resolved = sum(1 for c in complaints
                       if c["department"] == department
                       and c["status"] == "Resolved")
        normal(f"{department}: {count} total, {resolved} resolved")

    total = len(complaints)
    resolved_total = sum(1 for c in complaints if c["status"] == "Resolved")
    pending_total = total - resolved_total
    escalated_total = sum(1 for c in complaints if c["escalated"])

    print(BG_BLACK + MAUVE + BOLD + "\nOVERALL SUMMARY" + RESET)
    normal(f"Total complaints: {total}")
    normal(f"Resolved: {resolved_total}")
    normal(f"Pending: {pending_total}")
    normal(f"Escalated: {escalated_total}")


# -------------------- CITIZEN DASHBOARD --------------------
def citizen_dashboard(username):
    while True:
        heading("CITIZEN DASHBOARD")
        print(BG_BLACK + MAUVE + BOLD
              + f"Welcome, {username}!" + RESET)
        menu_option(1, "Register Complaint", True)
        menu_option(2, "View My Complaints")
        menu_option(3, "Check Complaint Status")
        menu_option(4, "Logout")
        choice = input(BG_BLACK + BEIGE + "\nEnter your choice: " + RESET).strip()

        if choice == "1":
            register_complaint(owner=username)
        elif choice == "2":
            view_my_complaints(username)
        elif choice == "3":
            check_my_status(username)
        elif choice == "4":
            success("Citizen logged out.")
            break
        else:
            error("Invalid choice. Please enter 1 to 4.")
        pause()


# -------------------- ADMIN DASHBOARD --------------------
def administrator_dashboard():
    while True:
        heading("ADMINISTRATOR DASHBOARD")
        menu_option(1, "View All Complaints", True)
        menu_option(2, "Update Complaint Status")
        menu_option(3, "Escalate Pending Complaints")
        menu_option(4, "View Statistics")
        menu_option(5, "Logout")
        choice = input(BG_BLACK + BEIGE + "\nEnter your choice: " + RESET).strip()

        if choice == "1":
            view_complaints()
        elif choice == "2":
            update_status()
        elif choice == "3":
            escalate_complaints()
        elif choice == "4":
            view_statistics()
        elif choice == "5":
            success("Administrator logged out.")
            break
        else:
            error("Invalid choice. Please enter 1 to 5.")
        pause()


# -------------------- LOGIN / MAIN MENU --------------------
def login_menu():
    heading("CIVICCONNECT")
    print(BG_BLACK + MAUVE + BOLD
          + "Complaint Routing & Escalation System" + RESET)
    print(BG_BLACK + HIGHLIGHT + HIGHLIGHT_TEXT + BOLD
          + "\nLOGIN PORTAL" + RESET)
    menu_option(1, "Citizen Registration", True)
    menu_option(2, "Citizen Login")
    menu_option(3, "Administrator Login")
    menu_option(4, "Exit")


def main():
    load_complaints()

    while True:
        login_menu()
        choice = input(BG_BLACK + BEIGE + BOLD
                       + "\nEnter your choice: " + RESET).strip()

        if choice == "1":
            register_citizen()
            pause()
        elif choice == "2":
            username = citizen_login()
            if username:
                pause()
                citizen_dashboard(username)
        elif choice == "3":
            if administrator_login():
                pause()
                administrator_dashboard()
            else:
                pause()
        elif choice == "4":
            success("Thank you for using CivicConnect!")
            break
        else:
            error("Invalid choice. Please enter 1 to 4.")
            pause()


if __name__ == "__main__":
    main()
