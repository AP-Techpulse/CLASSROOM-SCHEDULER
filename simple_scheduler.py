"""
SIMPLE CLASSROOM SCHEDULER - Computer Science Department
For 100-400 Level Courses
"""

import json

# ============================================================================
# HARDCODED DATA - Time Slots and Classrooms
# ============================================================================

# Time slots (Monday to Friday, 8 AM - 4 PM, 2-hour blocks)
# Wednesday ends at 12 PM
TIME_SLOTS = [
    ("Monday", "8 AM - 10 AM"),
    ("Monday", "10 AM - 12 PM"),
    ("Monday", "12 PM - 2 PM"),
    ("Monday", "2 PM - 4 PM"),
    
    ("Tuesday", "8 AM - 10 AM"),
    ("Tuesday", "10 AM - 12 PM"),
    ("Tuesday", "12 PM - 2 PM"),
    ("Tuesday", "2 PM - 4 PM"),
    
    ("Wednesday", "8 AM - 10 AM"),
    ("Wednesday", "10 AM - 12 PM"),
    
    ("Thursday", "8 AM - 10 AM"),
    ("Thursday", "10 AM - 12 PM"),
    ("Thursday", "12 PM - 2 PM"),
    ("Thursday", "2 PM - 4 PM"),
    
    ("Friday", "8 AM - 10 AM"),
    ("Friday", "10 AM - 12 PM"),
    ("Friday", "12 PM - 2 PM"),
    ("Friday", "2 PM - 4 PM"),
]

# Classrooms available in CS Department
CLASSROOMS = [
    {"name": "Software Lab", "capacity": 90},
    {"name": "Hardware Lab", "capacity": 80},
    {"name": "CS Lecture Hall 1", "capacity": 200},
    {"name": "CS Lecture Hall 2", "capacity": 150},
    {"name": "Tutorial Room A", "capacity": 50},
    {"name": "Tutorial Room B", "capacity": 50},
    {"name": "Seminar Room", "capacity": 100},
]

# CS Department Levels
LEVELS = [100, 200, 300, 400]


# ============================================================================
# SIMPLE SCHEDULING ALGORITHM
# ============================================================================

def load_user_data():
    """Load courses and lecturers from user input file"""
    try:
        with open('user_input.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"courses": [], "lecturers": []}


def calculate_sessions_needed(hours_per_week):
    """Calculate how many 2-hour sessions are needed"""
    return (hours_per_week + 1) // 2  # Round up


def schedule_courses():
    """
    Main scheduling function - Simple Greedy First-Fit Algorithm
    """
    # Load user input
    data = load_user_data()
    courses = data.get('courses', [])
    lecturers_data = data.get('lecturers', [])
    
    if not courses:
        return {
            "schedule": [],
            "unscheduled": [],
            "message": "No courses to schedule. Please add courses first."
        }
    
    # Build lecturer lookup
    lecturers = {}
    for lec in lecturers_data:
        lecturers[lec['name']] = {
            'hours_available': lec['hours_per_week'],
            'hours_used': 0
        }
    
    # Track what's been used
    room_usage = {}  # {(room_name, day, time): True}
    lecturer_usage = {}  # {(lecturer_name, day, time): True}
    level_usage = {}  # {(level, day, time): True}
    
    schedule = []
    unscheduled = []
    
    # Process each course
    for course in courses:
        assigned = False
        sessions_needed = calculate_sessions_needed(course['hours_per_week'])
        sessions_assigned = 0
        
        lecturer_name = course['lecturer']
        level = course['level']
        
        # Check if lecturer exists
        if lecturer_name not in lecturers:
            unscheduled.append({
                **course,
                "reason": f"Lecturer {lecturer_name} not found in system"
            })
            continue
        
        # Try to assign all needed sessions
        for day, time in TIME_SLOTS:
            if sessions_assigned >= sessions_needed:
                break
            
            # Check if lecturer has hours available
            if lecturers[lecturer_name]['hours_used'] >= lecturers[lecturer_name]['hours_available']:
                continue
            
            # Check if lecturer is already teaching at this time
            if (lecturer_name, day, time) in lecturer_usage:
                continue
            
            # Check if students at this level have class at this time
            if (level, day, time) in level_usage:
                continue
            
            # Find a suitable classroom
            room_found = False
            for room in sorted(CLASSROOMS, key=lambda r: r['capacity']):
                # Check if room can fit students (at least 80% capacity)
                if room['capacity'] < course['enrollment'] * 0.8:
                    continue
                
                # Check if room is available
                if (room['name'], day, time) in room_usage:
                    continue
                
                # Assign the class!
                schedule.append({
                    "course": course['course_code'],
                    "title": course['title'],
                    "level": level,
                    "lecturer": lecturer_name,
                    "room": room['name'],
                    "day": day,
                    "time": time,
                    "capacity": room['capacity'],
                    "enrollment": course['enrollment']
                })
                
                # Mark as used
                room_usage[(room['name'], day, time)] = True
                lecturer_usage[(lecturer_name, day, time)] = True
                level_usage[(level, day, time)] = True
                lecturers[lecturer_name]['hours_used'] += 2
                
                sessions_assigned += 1
                room_found = True
                break
            
            if not room_found:
                # No room available at this slot
                continue
        
        if sessions_assigned < sessions_needed:
            unscheduled.append({
                **course,
                "sessions_assigned": sessions_assigned,
                "sessions_needed": sessions_needed,
                "reason": f"Could only schedule {sessions_assigned}/{sessions_needed} sessions"
            })
        
        if sessions_assigned > 0:
            assigned = True
    
    # Calculate statistics
    total_courses = len(courses)
    scheduled_courses = len([c for c in courses if c['course_code'] in [s['course'] for s in schedule]])
    
    stats = {
        "total_courses": total_courses,
        "fully_scheduled": scheduled_courses - len(unscheduled),
        "partially_scheduled": len([u for u in unscheduled if u.get('sessions_assigned', 0) > 0]),
        "unscheduled": len([u for u in unscheduled if u.get('sessions_assigned', 0) == 0]),
        "success_rate": round((scheduled_courses / total_courses * 100) if total_courses > 0 else 0, 1),
        "total_sessions": len(schedule)
    }
    
    return {
        "schedule": schedule,
        "unscheduled": unscheduled,
        "statistics": stats,
        "lecturer_workload": {name: data['hours_used'] for name, data in lecturers.items()}
    }


def print_schedule():
    """Print the schedule in a nice format"""
    result = schedule_courses()
    
    print("\n" + "="*100)
    print("COMPUTER SCIENCE DEPARTMENT - CLASSROOM SCHEDULE")
    print("Levels: 100, 200, 300, 400")
    print("="*100 + "\n")
    
    if not result['schedule']:
        print(result.get('message', 'No schedule generated.'))
        return
    
    # Group by level
    for level in LEVELS:
        level_schedule = [s for s in result['schedule'] if s['level'] == level]
        if level_schedule:
            print(f"\n{level} LEVEL COURSES")
            print("-"*100)
            print(f"{'Course':<12} {'Title':<30} {'Day':<10} {'Time':<15} {'Room':<20} {'Lecturer':<20}")
            print("-"*100)
            for entry in sorted(level_schedule, key=lambda x: (x['day'], x['time'])):
                print(f"{entry['course']:<12} {entry['title'][:28]:<30} {entry['day']:<10} "
                      f"{entry['time']:<15} {entry['room']:<20} {entry['lecturer']:<20}")
    
    # Show unscheduled
    if result['unscheduled']:
        print("\n" + "="*100)
        print("UNSCHEDULED / PARTIALLY SCHEDULED COURSES")
        print("-"*100)
        for item in result['unscheduled']:
            print(f"• {item['course_code']}: {item['title']} - {item['reason']}")
    
    # Show statistics
    print("\n" + "="*100)
    print("STATISTICS")
    print("-"*100)
    stats = result['statistics']
    print(f"Total Courses: {stats['total_courses']}")
    print(f"Fully Scheduled: {stats['fully_scheduled']}")
    print(f"Partially Scheduled: {stats['partially_scheduled']}")
    print(f"Unscheduled: {stats['unscheduled']}")
    print(f"Success Rate: {stats['success_rate']}%")
    print(f"Total Sessions: {stats['total_sessions']}")
    
    # Lecturer workload
    print("\n" + "="*100)
    print("LECTURER WORKLOAD")
    print("-"*100)
    for lecturer, hours in result['lecturer_workload'].items():
        print(f"{lecturer}: {hours} hours")
    
    print("\n" + "="*100)


def save_schedule_to_file():
    """Save schedule to JSON file"""
    result = schedule_courses()
    with open('schedule_output.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("Schedule saved to: schedule_output.json")


if __name__ == "__main__":
    print_schedule()
    save_schedule_to_file()
