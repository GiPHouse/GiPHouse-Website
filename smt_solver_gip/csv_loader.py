import csv
import sys

import engineer_data
import project_data
from colour_codes import *
from collections import defaultdict

EXPECTED_COLUMNS = [
    "First name",
    "Last name",
    "Student number",
    "GitHub username",
    "Course",
    "1st project preference",
    "2nd project preference",
    "3rd project preference",
    "1st partner preference",
    "2nd partner preference",
    "3rd partner preference",
    "Dev Experience",
    "Git Experience",
    "Scrum Experience",
    "Management Interest",
    "Non-dutch",
    "Available during scheduled timeslot 1",
    "Available during scheduled timeslot 2",
    "Available during scheduled timeslot 3",
    "Available during scheduled timeslot 4",
    "Available during scheduled timeslot 5",
    "Available during scheduled timeslot 6",
    "Available during scheduled timeslot 7",
    "Available during scheduled timeslot 8",
    "Available during scheduled timeslot 9",
    "Available during scheduled timeslot 10",
    "Has problems with signing an NDA",
    "Registration Comments",
]

PROJECT_PREFERENCE_COLUMNS = [
    "1st project preference",
    "2nd project preference",
    "3rd project preference",
]

EXPERIENCE_COLUMNS = [
    "Dev Experience",
    "Git Experience",
    "Scrum Experience",
]

BOOLEAN_COLUMNS = [
    "Management Interest",
    "Non-dutch",
    "Available during scheduled timeslot 1",
    "Available during scheduled timeslot 2",
    "Available during scheduled timeslot 3",
    "Available during scheduled timeslot 4",
    "Available during scheduled timeslot 5",
    "Available during scheduled timeslot 6",
    "Available during scheduled timeslot 7",
    "Available during scheduled timeslot 8",
    "Available during scheduled timeslot 9",
    "Available during scheduled timeslot 10",
    "Has problems with signing an NDA",
]

TIMESLOT_COLUMNS = [
    "Available during scheduled timeslot 1",
    "Available during scheduled timeslot 2",
    "Available during scheduled timeslot 3",
    "Available during scheduled timeslot 4",
    "Available during scheduled timeslot 5",
    "Available during scheduled timeslot 6",
    "Available during scheduled timeslot 7",
    "Available during scheduled timeslot 8",
    "Available during scheduled timeslot 9",
    "Available during scheduled timeslot 10",
]

VALID_COURSES = [
    "Software Engineering",
    "System Development Management",
    "Software Development Entrepreneurship",
]

def parse_exp(value):
    if value == "Beginner":
        return engineer_data.BEGINNER
    elif value == "Junior":
        return engineer_data.JUNIOR
    elif value == "Intermediate":
        return engineer_data.INTERMEDIATE
    elif value == "Pretty Good":
        return engineer_data.PRETTY_GOOD
    elif value == "Advanced":
        return engineer_data.ADVANCED
    return value

def parse_booleans(value):
    if value == "True":
        return True
    elif value == "False":
        return False
    return value

def parse_timetable(row):
    slots = []
    if row["Available during scheduled timeslot 1"] == "True":
        slots.append((engineer_data.MONDAY, 1))
    if row["Available during scheduled timeslot 2"] == "True":
        slots.append((engineer_data.MONDAY, 2))
    if row["Available during scheduled timeslot 3"] == "True":
        slots.append((engineer_data.TUESDAY, 1))
    if row["Available during scheduled timeslot 4"] == "True":
        slots.append((engineer_data.TUESDAY, 2))
    if row["Available during scheduled timeslot 5"] == "True":
        slots.append((engineer_data.WEDNESDAY, 1))
    if row["Available during scheduled timeslot 6"] == "True":
        slots.append((engineer_data.WEDNESDAY, 2))
    if row["Available during scheduled timeslot 7"] == "True":
        slots.append((engineer_data.THURSDAY, 1))
    if row["Available during scheduled timeslot 8"] == "True":
        slots.append((engineer_data.THURSDAY, 2))
    if row["Available during scheduled timeslot 9"] == "True":
        slots.append((engineer_data.FRIDAY, 1))
    if row["Available during scheduled timeslot 10"] == "True":
        slots.append((engineer_data.FRIDAY, 2))
    return slots

def verify_columns(header):
    missing = [col for col in EXPECTED_COLUMNS if col not in header]
    unexpected = [col for col in header if col not in EXPECTED_COLUMNS]
    if missing:
        print(f"{RED}Error: Missing columns: {', '.join(missing)}{RESET}")
    if unexpected:
        print(f"{RED}Error: Unexpected columns: {', '.join(unexpected)}{RESET}")


def verify_row(row):
    errors = []
    
    name = row['First name'] + " " + row['Last name']
    
    if row["Course"] not in VALID_COURSES:
        errors.append(f"Invalid course '{row['Course']}' for student {name}")
    
    for col in PROJECT_PREFERENCE_COLUMNS:
        if row[col] != "" and row[col] not in project_data.full_names and row[col] not in project_data.short_names:
            errors.append(f"Invalid project preference '{row[col]}' in column {col} for student {name}")
    
    for col in EXPERIENCE_COLUMNS:
        if row[col] not in ["Beginner", "Junior", "Intermediate", "Pretty Good", "Advanced"]:
            errors.append(f"Invalid experience level '{row[col]}' in column {col} for student {name}")
    
    for col in BOOLEAN_COLUMNS:
        if row[col] not in ["True", "False"]:
            errors.append(f"Invalid boolean value '{row[col]}' in column {col} for student {name}")
    
    return name, errors

managers = []
friend_data = []
all_errors = defaultdict(list)

def load_registrations(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.fieldnames
        verify_columns(header)
        for row in reader:
            name, errors = verify_row(row)
            if errors:
                all_errors[name].extend(errors)
            elif row['Course'] == 'Software Engineering':
                engineer_data.add_student(
                    name,
                    parse_exp(row["Dev Experience"]),
                    parse_booleans(row["Management Interest"]),
                    parse_booleans(row["Non-dutch"]),
                    parse_booleans(row["Has problems with signing an NDA"]),
                    parse_timetable(row),
                    [p for p in [row["1st project preference"],
                                row["2nd project preference"],
                                row["3rd project preference"]] if p != ""]
                )
                partners = [row["1st partner preference"],
                            row["2nd partner preference"],
                            row["3rd partner preference"]]
                while "" in partners: partners.remove("")
                friend_data.append((name, partners))
            else:
                managers.append(row)

    if all_errors:
        print(f"{RED}The following students were skipped due to invalid data:{RESET}")
        for name, errors in all_errors.items():
            print(f"{RED}  {name}:{RESET}")
            for error in errors:
                print(f"{RED}    - {error}{RESET}")

        skipped = set(all_errors.keys())
        for i in range(len(friend_data)):
            friend_data[i] = (friend_data[i][0], 
                            [f for f in friend_data[i][1] if f not in skipped])

def get_friend_data():
    return friend_data

def print_manager(manager, prestring, highlight):
    col = BROWN
    if highlight: col = YELLOW
    name = manager['First name'] + " " + manager['Last name']
    print(prestring + col + name + RESET + " likes", end="")
    prefs = [manager['1st project preference'], manager['2nd project preference'], manager['3rd project preference']]
    prefs = [p for p in prefs if p != ""]
    for i in range(len(prefs)):
        if i != 0: print(",", end="")
        print(" " + prefs[i], end="")
    ccode = ""
    exp = parse_exp(manager['Dev Experience'])
    if exp >= engineer_data.ADVANCED: ccode = GREEN
    elif exp >= engineer_data.INTERMEDIATE: ccode = DARKGREEN
    print(" ; " + ccode + "lvl " + str(exp) + RESET, end="")
    if manager['Management Interest'] == 'True': print(" ; " + CYAN + "management" + RESET, end="")
    if manager['Non-dutch'] == 'True': print(" ; " + PURPLE + "international" + RESET, end="")
    if manager['Has problems with signing an NDA'] == 'True': print(" ; " + BRED + "no NDA" + RESET, end="")
    print("; available: ", end="")
    slots = parse_timetable(manager)
    for pair in slots: print(pair[0] + str(pair[1]), end=" ")
    print()

def get_managers():
    return managers

def print_managers(lst, prestring):
    for manager in lst: print_manager(manager, prestring, False)

def print_registrations(registrations):
    for reg in registrations:
        print(reg)

def get_header(registrations):
    if len(registrations) == 0:
        return []
    return list(registrations[0].keys())


# registrations = load_registrations('test_registrations.csv')
# header = get_header(registrations)

# print(f"CSV Header: {header}")

# engineers = get_engineers(registrations)
# print(f"Engineers: {engineers}")

