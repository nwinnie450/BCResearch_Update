#!/usr/bin/env python3
"""
Create Mock Data for Testing Schedule and Notification System
"""
import json
import os
from datetime import datetime, timedelta
import random

def create_mock_schedules():
    """Create sample schedules for testing"""
    
    mock_schedules = [
        {
            "id": "20241216_090000",
            "name": "Daily Morning Check",
            "frequency": "Daily (Every day)",
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "days_display": "Every day",
            "time": "9:00 AM",
            "time_24h": "09:00",
            "enabled": True,
            "created_date": "2024-12-16",
            "created_at": "2024-12-16T09:00:00"
        },
        {
            "id": "20241216_130000",
            "name": "Weekday Afternoon Check",
            "frequency": "Weekdays (Monday-Friday)",
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "days_display": "Monday-Friday",
            "time": "1:00 PM",
            "time_24h": "13:00",
            "enabled": True,
            "created_date": "2024-12-16",
            "created_at": "2024-12-16T13:00:00"
        },
        {
            "id": "20241216_170000",
            "name": "Monday Weekly Review",
            "frequency": "Weekly (Once per week)",
            "days": ["Monday"],
            "days_display": "Every Monday",
            "time": "5:00 PM",
            "time_24h": "17:00",
            "enabled": True,
            "created_date": "2024-12-16",
            "created_at": "2024-12-16T17:00:00"
        },
        {
            "id": "20241216_100000",
            "name": "Custom Weekend Check",
            "frequency": "Custom (Select specific days)",
            "days": ["Saturday", "Sunday"],
            "days_display": "Saturday, Sunday",
            "time": "10:00 AM",
            "time_24h": "10:00",
            "enabled": False,  # Disabled for testing
            "created_date": "2024-12-16",
            "created_at": "2024-12-16T10:00:00"
        }
    ]
    
    # Save mock schedules
    os.makedirs("data", exist_ok=True)
    with open("data/simple_schedules.json", 'w') as f:
        json.dump(mock_schedules, f, indent=2)
    
    print(f"Created {len(mock_schedules)} mock schedules")
    print("   - Daily Morning Check (9:00 AM)")
    print("   - Weekday Afternoon Check (1:00 PM)")
    print("   - Monday Weekly Review (5:00 PM)")
    print("   - Custom Weekend Check (10:00 AM) - Disabled")
    
    return mock_schedules

def create_mock_proposal_data():
    """Create mock proposal data for all protocols"""
    
    protocols = {
        'eips': {
            'protocol': 'Ethereum',
            'count': 15,
            'source': 'Mock Data',
            'items': []
        },
        'tips': {
            'protocol': 'Tron',
            'count': 12,
            'source': 'Mock Data',
            'items': []
        },
        'bips': {
            'protocol': 'Bitcoin',
            'count': 8,
            'source': 'Mock Data',
            'items': []
        },
        'beps': {
            'protocol': 'Binance Smart Chain',
            'count': 6,
            'source': 'Mock Data',
            'items': []
        }
    }
    
    # Create mock proposals for each protocol
    for protocol_key, protocol_data in protocols.items():
        items = []
        
        for i in range(protocol_data['count']):
            proposal_number = 7000 + (i * 10) + random.randint(1, 9)
            
            items.append({
                'number': proposal_number,
                'title': f'Mock {protocol_data["protocol"]} Proposal {proposal_number}',
                'status': random.choice(['draft', 'final', 'active', 'withdrawn']),
                'created': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'author': f'Developer{random.randint(1, 10)}',
                'summary': f'This is a mock proposal for testing the {protocol_data["protocol"]} notification system.',
                'type': protocol_key.upper()[:-1]  # EIP, TIP, BIP, BEP
            })
        
        # Sort by number descending (newest first)
        items.sort(key=lambda x: x['number'], reverse=True)
        
        protocol_data['items'] = items
        protocol_data['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        protocol_data['generated_at_iso'] = datetime.now().isoformat()
    
    # Save mock data files
    os.makedirs("data", exist_ok=True)
    
    file_mapping = {
        'eips': 'eips.json',
        'tips': 'tips.json', 
        'bips': 'bips.json',
        'beps': 'beps.json'
    }
    
    for protocol_key, filename in file_mapping.items():
        with open(f"data/{filename}", 'w') as f:
            json.dump(protocols[protocol_key], f, indent=2)
        
        print(f"Created {filename} with {protocols[protocol_key]['count']} mock proposals")
    
    return protocols

def create_mock_last_check():
    """Create a mock last check file to simulate previous state"""
    
    # Create a previous state with fewer proposals to simulate new ones
    previous_proposals = {
        'ethereum': set(range(7001, 7010)),  # 9 proposals
        'tron': set(range(7001, 7008)),      # 7 proposals  
        'bitcoin': set(range(7001, 7005)),   # 4 proposals
        'binance_smart_chain': set(range(7001, 7004))  # 3 proposals
    }
    
    # Convert sets to lists for JSON serialization
    serializable_data = {}
    for protocol, proposal_set in previous_proposals.items():
        serializable_data[protocol] = list(proposal_set)
    
    last_check_data = {
        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
        'proposals': serializable_data
    }
    
    with open("data/last_proposal_check.json", 'w') as f:
        json.dump(last_check_data, f, indent=2)
    
    print("Created mock last check data (simulates previous state)")
    print("   - This will make new proposals appear as 'new' during testing")
    
    return last_check_data

def simulate_new_proposals():
    """Add a few new proposals to simulate updates"""
    
    protocols_to_update = ['eips', 'tips']
    
    for protocol in protocols_to_update:
        filename = f"data/{protocol}.json"
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Add 1-2 new proposals
            new_count = random.randint(1, 2)
            existing_numbers = [item['number'] for item in data['items']]
            max_number = max(existing_numbers) if existing_numbers else 7000
            
            for i in range(new_count):
                new_number = max_number + i + 1
                data['items'].insert(0, {  # Insert at beginning (newest first)
                    'number': new_number,
                    'title': f'BRAND NEW {data["protocol"]} Proposal {new_number}',
                    'status': 'draft',
                    'created': datetime.now().strftime('%Y-%m-%d'),
                    'author': 'TestDeveloper',
                    'summary': f'This is a brand new proposal added for testing notifications!',
                    'type': protocol.upper()[:-1]
                })
            
            data['count'] = len(data['items'])
            data['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            data['generated_at_iso'] = datetime.now().isoformat()
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Added {new_count} new proposals to {protocol}")

def create_test_schedule_in_near_future():
    """Create a test schedule that runs in the next few minutes"""
    
    # Calculate time 2 minutes from now
    future_time = datetime.now() + timedelta(minutes=2)
    time_str = future_time.strftime('%H:%M')
    time_display = future_time.strftime('%I:%M %p')
    
    test_schedule = {
        "id": f"test_{int(future_time.timestamp())}",
        "name": "Test Schedule (2 minutes)",
        "frequency": "Custom (Select specific days)",
        "days": [future_time.strftime('%A')],  # Today's day
        "days_display": f"Every {future_time.strftime('%A')}",
        "time": time_display,
        "time_24h": time_str,
        "enabled": True,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat()
    }
    
    # Load existing schedules
    schedules = []
    if os.path.exists("data/simple_schedules.json"):
        with open("data/simple_schedules.json", 'r') as f:
            schedules = json.load(f)
    
    # Add test schedule
    schedules.append(test_schedule)
    
    with open("data/simple_schedules.json", 'w') as f:
        json.dump(schedules, f, indent=2)
    
    print(f"Created test schedule that will run at {time_display} (in ~2 minutes)")
    print(f"   Schedule name: '{test_schedule['name']}'")
    
    return test_schedule

def main():
    """Create all mock data"""
    print("Creating Mock Data for Testing...")
    print("=" * 50)
    
    # Create mock schedules
    print("\nCreating Mock Schedules...")
    create_mock_schedules()
    
    # Create mock proposal data
    print("\nCreating Mock Proposal Data...")
    create_mock_proposal_data()
    
    # Create mock last check (previous state)
    print("\nCreating Mock Previous State...")
    create_mock_last_check()
    
    # Simulate some new proposals
    print("\nSimulating New Proposals...")
    simulate_new_proposals()
    
    # Create test schedule for immediate testing
    print("\nCreating Near-Future Test Schedule...")
    create_test_schedule_in_near_future()
    
    print("\n" + "=" * 50)
    print("Mock Data Creation Complete!")
    print("\nWhat was created:")
    print("   - Sample schedules (daily, weekday, weekly, custom)")
    print("   - Mock proposal data for all protocols")
    print("   - Previous state data (for comparison)")
    print("   - New proposals (to trigger notifications)")
    print("   - Test schedule (runs in 2 minutes)")
    
    print("\nHow to test:")
    print("   1. Go to Schedule page")
    print("   2. Click 'Start Scheduler'")
    print("   3. Click 'Test Check' to see immediate notifications")
    print("   4. Wait 2 minutes for automatic scheduled test")
    print("   5. Check for desktop notifications!")

if __name__ == "__main__":
    main()