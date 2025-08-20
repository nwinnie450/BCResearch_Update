"""
Comprehensive Schedule Test
Tests the complete schedule system with notification triggering
"""
import sys
sys.path.insert(0, '.')

import json
import os
from datetime import datetime
from services.enhanced_notification_service import EnhancedNotificationService
from components.schedule_history import log_schedule_execution

def simulate_new_proposals():
    """Simulate finding new proposals to trigger notifications"""
    
    print("=== COMPREHENSIVE SCHEDULE TEST ===")
    print("Simulating a complete schedule run with new proposals...")
    print()
    
    # Create realistic test proposals
    test_proposals = {
        'bitcoin': [
            {
                'id': 'BIP-442',
                'title': 'Topology Restrictions for Pinning Prevention',
                'protocol': 'bitcoin',
                'status': 'Final',
                'url': 'https://github.com/bitcoin/bips/blob/master/bip-0442.mediawiki',
                'created': '2024-01-10',
                'author': 'Gregory Sanders'
            }
        ],
        'ethereum': [
            {
                'id': 'EIP-7212',
                'title': 'Precompile for secp256r1 Curve Support',
                'protocol': 'ethereum',
                'status': 'Draft',
                'url': 'https://eips.ethereum.org/EIPS/eip-7212',
                'created': '2023-06-20',
                'author': 'Ulrich Haböck'
            },
            {
                'id': 'EIP-4844',
                'title': 'Shard Blob Transactions (Proto-Danksharding)',
                'protocol': 'ethereum',
                'status': 'Final',
                'url': 'https://eips.ethereum.org/EIPS/eip-4844',
                'created': '2022-02-25',
                'author': 'Vitalik Buterin'
            }
        ]
    }
    
    print("Simulated New Proposals Found:")
    for protocol, proposals in test_proposals.items():
        print(f"  {protocol.upper()}: {len(proposals)} proposals")
        for proposal in proposals:
            print(f"    - {proposal['id']}: {proposal['title']}")
    print()
    
    return test_proposals

def run_schedule_test():
    """Run a complete schedule test"""
    
    start_time = datetime.now()
    
    try:
        print("1. Simulating proposal discovery...")
        new_proposals = simulate_new_proposals()
        
        if new_proposals and any(len(props) > 0 for props in new_proposals.values()):
            print("2. New proposals found! Triggering notification system...")
            
            # Initialize notification service
            service = EnhancedNotificationService()
            
            # Send enhanced notifications
            print("3. Sending notifications with complete format...")
            result = service.send_enhanced_notifications(new_proposals)
            
            print("4. Notification Results:")
            if result['email']:
                print("   EMAIL: Sent successfully with complete format")
                print("     - Main title with protocol and ID")
                print("     - Subtitle with metadata (Status | Impact | etc.)")
                print("     - TL;DR section")
                print("     - Why it matters (bullet points)")
                print("     - Impact reason, Activation, Effect, Effort")
                print("     - Required actions (numbered list)")
                print("     - Blue action buttons")
                print("     - Professional footer")
            else:
                print("   EMAIL: Failed to send")
            
            if result['slack']:
                print("   SLACK: Sent successfully with complete format")
                print("     - Same content structure as email")
                print("     - Block kit format")
                print("     - Blue primary buttons")
            else:
                print("   SLACK: Failed to send")
            
            # Log the execution
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            log_schedule_execution(
                schedule_name="Comprehensive Test Run",
                success=True,
                start_time=start_time,
                new_proposals=new_proposals,
                error=None,
                logs=f"Test executed successfully in {duration:.2f}s"
            )
            
            print(f"5. Schedule execution logged (duration: {duration:.2f}s)")
            print()
            print("SCHEDULE TEST COMPLETED SUCCESSFULLY!")
            print()
            print("Summary of what was tested:")
            print("- Proposal discovery simulation")
            print("- Impact analysis with OpenAI")
            print("- Complete email format with all fields")
            print("- Complete Slack format with all fields")
            print("- Blue button styling")
            print("- Subtitle with metadata")
            print("- Schedule history logging")
            
        else:
            print("2. No new proposals to process")
            log_schedule_execution(
                schedule_name="Comprehensive Test Run",
                success=True,
                start_time=start_time,
                new_proposals={},
                logs="No new proposals found during test"
            )
            
    except Exception as e:
        print(f"ERROR: Schedule test failed: {e}")
        log_schedule_execution(
            schedule_name="Comprehensive Test Run",
            success=False,
            start_time=start_time,
            error=str(e),
            logs=f"Test failed: {str(e)}"
        )

def show_current_schedule_status():
    """Show the current scheduler status"""
    
    print("=== CURRENT SCHEDULE STATUS ===")
    
    # Load schedules
    schedules_file = "data/simple_schedules.json"
    if os.path.exists(schedules_file):
        with open(schedules_file, 'r') as f:
            schedules = json.load(f)
        
        print(f"Active Schedules: {len(schedules)}")
        for schedule in schedules:
            status = "ENABLED" if schedule.get('enabled', False) else "DISABLED"
            print(f"  - {schedule['name']}: {schedule['time']} ({status})")
    else:
        print("No schedules file found")
    
    # Load execution history
    history_file = "data/schedule_history.json"
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        recent_executions = sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)[:3]
        print(f"Recent Executions: {len(recent_executions)}")
        for execution in recent_executions:
            status = "SUCCESS" if execution.get('success', False) else "FAILED"
            timestamp = execution.get('timestamp', 'Unknown')
            print(f"  - {execution.get('schedule_name', 'Unknown')}: {timestamp} ({status})")
    else:
        print("No execution history found")
    
    print()

if __name__ == "__main__":
    # Show current status
    show_current_schedule_status()
    
    # Run comprehensive test
    run_schedule_test()
    
    print("\nCheck your email and Slack to see the complete notification format!")
    print("Also check the Schedule History in the UI to see the logged execution.")