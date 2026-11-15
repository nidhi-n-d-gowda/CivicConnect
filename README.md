# CivicConnect – Complaint Routing and Escalation System

## Project Overview
CivicConnect is a Python console application that helps citizens register civic complaints such as potholes, garbage collection issues, and street-light problems. It automatically routes complaints to the appropriate department and supports complaint tracking and escalation.

## Problem Statement
Civic complaints can be delayed or lost when they are not sent to the correct department or tracked properly. CivicConnect provides a simple system to register, route, track, and report complaints.

## Objectives
- Register complaints with category, ward, and description.
- Automatically assign complaints to the appropriate department.
- Track complaint status.
- Escalate complaints pending beyond a configured number of days.
- Display ward-wise and department-wise statistics.

## Core Features
1. Complaint registration
2. Automatic department routing
3. Status updates: Received, Assigned, In Progress, Resolved
4. Pending complaint escalation
5. Ward-wise and department-wise statistics

## Technologies Used
- Python
- VS Code
- Text-file storage

## Department Routing
| Category | Department |
|---|---|
| Pothole | Roads Department |
| Garbage | Sanitation Department |
| Street Light | Electrical Department |
| Water Supply | Water Department |
| Other | Municipal Department |

## How to Run
1. Install Python 3.
2. Open this folder in VS Code.
3. Open the terminal in the project folder.
4. Run:

   ```bash
   python app.py
   ```

5. Follow the menu displayed in the terminal.

## Data Storage
Complaint records are saved in `complaints.txt` so they can be loaded when the application starts again.

## Escalation Rule
Unresolved complaints pending for more than 7 days are marked as escalated.

## Project Type
Menu-driven console application for the CP-073 capstone.
