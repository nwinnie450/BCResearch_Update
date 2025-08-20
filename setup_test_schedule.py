"""
Setup Test Schedule
Creates a schedule that runs soon for testing purposes
"""
import sys
sys.path.insert(0, '.')

import json
import os
from datetime import datetime, timedelta

def setup_test_schedule():
    """Set up a test schedule that runs in the next few minutes"""
    
    print("=== SETTING UP TEST SCHEDULE ===")
    
    # Calculate time 2 minutes from now
    current_time = datetime.now()
    test_time = current_time + timedelta(minutes=2)
    
    # Format for 12-hour display
    time_12h = test_time.strftime("%I:%M %p").lstrip('0')
    time_24h = test_time.strftime("%H:%M")
    
    print(f"Current time: {current_time.strftime('%I:%M:%S %p')}")
    print(f"Setting up test schedule for: {time_12h}")
    print()
    
    # Create test schedule
    test_schedule = {
        "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "name": f"Test Schedule - {time_12h}",
        "frequency": "Daily (Every day)",
        "days": [
            "Monday", "Tuesday", "Wednesday", "Thursday", 
            "Friday", "Saturday", "Sunday"
        ],
        "days_display": "Every day",
        "time": time_12h,
        "time_24h": time_24h,
        "enabled": True,
        "created_date": current_time.strftime("%Y-%m-%d"),
        "created_at": current_time.isoformat()
    }
    
    # Load existing schedules
    schedules_file = "data/simple_schedules.json"
    schedules = []
    
    if os.path.exists(schedules_file):
        try:
            with open(schedules_file, 'r') as f:
                schedules = json.load(f)
        except:
            schedules = []
    
    # Add new test schedule
    schedules.append(test_schedule)
    
    # Save schedules
    os.makedirs("data", exist_ok=True)
    with open(schedules_file, 'w') as f:
        json.dump(schedules, f, indent=2)
    
    print("Test schedule created successfully!")
    print(f"Schedule ID: {test_schedule['id']}")
    print(f"Schedule Name: {test_schedule['name']}")
    print(f"Execution Time: {test_schedule['time']} ({test_schedule['time_24h']})")
    print(f"Status: {'ENABLED' if test_schedule['enabled'] else 'DISABLED'}")
    print()
    
    # Show all current schedules
    print("=== ALL CURRENT SCHEDULES ===")
    for i, schedule in enumerate(schedules, 1):
        status = "ENABLED" if schedule.get('enabled', False) else "DISABLED"
        print(f"{i}. {schedule['name']}")
        print(f"   Time: {schedule['time']} ({status})")
        print(f"   Frequency: {schedule['frequency']}")
        print()
    
    print("=== NEXT STEPS ===")
    print("1. The test schedule will run automatically in ~2 minutes")
    print("2. Make sure the scheduler is running:")
    print("   python start_scheduler.py")
    print("3. Watch for notifications in your email and Slack")
    print("4. Check the Schedule History tab in the UI for execution logs")
    print()
    print(f"Expected execution time: {time_12h}")
    print("The system will:")
    print("- Fetch latest proposals from all protocols")
    print("- Analyze them with AI-powered impact analysis")
    print("- Send complete email notification with all fields")
    print("- Send individual Slack notifications for each proposal")
    print("- Log the execution in schedule history")
    
    return test_schedule

def show_scheduler_status():
    """Show if scheduler is running"""
    print("=== SCHEDULER STATUS CHECK ===")
    
    # Try to read recent logs or check for running processes
    try:
        import psutil
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'start_scheduler.py' in cmdline:
                        python_processes.append(proc.info)
            except:
                continue
        
        if python_processes:
            print("Scheduler is running!")
            for proc in python_processes:
                print(f"  PID: {proc['pid']}")
        else:
            print("Scheduler not detected. Run: python start_scheduler.py")
            
    except ImportError:
        print("psutil not available - cannot check if scheduler is running")
        print("To start scheduler manually: python start_scheduler.py")
    
    print()

if __name__ == "__main__":
    show_scheduler_status()
    test_schedule = setup_test_schedule()
    
    print("Test schedule is ready!")
    print("Wait for the scheduled time and check your notifications!")