#!/usr/bin/env python3
"""
Real-Time Data Fetcher Service
Allows selective, real-time fetching of blockchain proposal data for specific protocols
"""
import subprocess
import sys
import time
import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path

class RealTimeDataFetcher:
    """Service for real-time fetching of blockchain proposal data"""
    
    def __init__(self):
        self.protocols = {
            'ethereum': {
                'name': 'Ethereum (EIPs)',
                'script': 'fetch_eips.py',
                'file': 'eips.json',
                'color': '#627EEA',
                'description': 'Ethereum Improvement Proposals'
            },
            'tron': {
                'name': 'Tron (TIPs)',
                'script': 'fetch_tips.py',
                'file': 'tips.json',
                'color': '#FF0013',
                'description': 'TRON Improvement Proposals'
            },
            'bitcoin': {
                'name': 'Bitcoin (BIPs)',
                'script': 'fetch_bips.py',
                'file': 'bips.json',
                'color': '#F7931A',
                'description': 'Bitcoin Improvement Proposals'
            },
            'binance_smart_chain': {
                'name': 'BSC (BEPs)',
                'script': 'fetch_beps.py',
                'file': 'beps.json',
                'color': '#F3BA2F',
                'description': 'BNB Chain Evolution Proposals'
            }
        }
        
        self.is_fetching = {}
        self.last_fetch_times = {}
        self.fetch_results = {}
        
        # Load last fetch times
        self._load_fetch_history()
    
    def get_protocol_list(self) -> List[Dict]:
        """Get list of available protocols with metadata"""
        protocol_list = []
        
        for protocol_id, config in self.protocols.items():
            # Get current data info
            data_info = self.get_protocol_info(protocol_id)
            
            protocol_list.append({
                'id': protocol_id,
                'name': config['name'],
                'description': config['description'],
                'color': config['color'],
                'file': config['file'],
                'is_fetching': self.is_fetching.get(protocol_id, False),
                'last_fetch': self.last_fetch_times.get(protocol_id),
                'current_count': data_info.get('count', 0),
                'last_updated': data_info.get('generated_at_iso', 'Never'),
                'status': self._get_protocol_status(protocol_id)
            })
        
        return protocol_list
    
    def get_protocol_info(self, protocol_id: str) -> Dict:
        """Get current information about a protocol's data"""
        if protocol_id not in self.protocols:
            return {}
        
        config = self.protocols[protocol_id]
        filepath = f"data/{config['file']}"
        
        if not os.path.exists(filepath):
            return {'count': 0, 'generated_at_iso': 'No data', 'status': 'missing'}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'count': data.get('count', 0),
                'protocol': data.get('protocol', protocol_id),
                'generated_at_iso': data.get('generated_at_iso', 'Unknown'),
                'source': data.get('source', 'Unknown'),
                'status': 'available'
            }
        except Exception as e:
            return {'count': 0, 'generated_at_iso': 'Error', 'status': 'error', 'error': str(e)}
    
    def _get_protocol_status(self, protocol_id: str) -> str:
        """Get the current status of a protocol"""
        if self.is_fetching.get(protocol_id, False):
            return 'fetching'
        
        info = self.get_protocol_info(protocol_id)
        return info.get('status', 'unknown')
    
    def fetch_protocol_data(self, protocol_id: str, callback=None) -> Dict:
        """Fetch data for a specific protocol"""
        if protocol_id not in self.protocols:
            return {'success': False, 'error': f'Unknown protocol: {protocol_id}'}
        
        if self.is_fetching.get(protocol_id, False):
            return {'success': False, 'error': f'{protocol_id} is already being fetched'}
        
        config = self.protocols[protocol_id]
        
        try:
            # Mark as fetching
            self.is_fetching[protocol_id] = True
            start_time = time.time()
            
            print(f"Starting real-time fetch for {config['name']}...")
            
            # Run the specific scraper script
            result = subprocess.run([
                sys.executable, f"scripts/{config['script']}"
            ], cwd='.', capture_output=True, text=True, timeout=300)
            
            fetch_duration = time.time() - start_time
            
            # Mark as no longer fetching
            self.is_fetching[protocol_id] = False
            
            if result.returncode == 0:
                # Update fetch time
                self.last_fetch_times[protocol_id] = datetime.now().isoformat()
                self._save_fetch_history()
                
                # Get updated info
                updated_info = self.get_protocol_info(protocol_id)
                
                result_data = {
                    'success': True,
                    'protocol': protocol_id,
                    'protocol_name': config['name'],
                    'duration': round(fetch_duration, 2),
                    'count': updated_info.get('count', 0),
                    'generated_at': updated_info.get('generated_at_iso', 'Unknown'),
                    'message': f"Successfully fetched {updated_info.get('count', 0)} {config['description']}"
                }
                
                self.fetch_results[protocol_id] = result_data
                
                if callback:
                    callback(result_data)
                
                return result_data
            else:
                error_data = {
                    'success': False,
                    'protocol': protocol_id,
                    'protocol_name': config['name'],
                    'duration': round(fetch_duration, 2),
                    'error': f"Fetch failed: {result.stderr or 'Unknown error'}",
                    'stdout': result.stdout
                }
                
                self.fetch_results[protocol_id] = error_data
                
                if callback:
                    callback(error_data)
                
                return error_data
                
        except Exception as e:
            self.is_fetching[protocol_id] = False
            error_data = {
                'success': False,
                'protocol': protocol_id,
                'protocol_name': config['name'],
                'error': f"Exception during fetch: {str(e)}"
            }
            
            self.fetch_results[protocol_id] = error_data
            
            if callback:
                callback(error_data)
            
            return error_data
    
    def fetch_multiple_protocols(self, protocol_ids: List[str], callback=None) -> Dict:
        """Fetch data for multiple protocols in parallel"""
        if not protocol_ids:
            return {'success': False, 'error': 'No protocols specified'}
        
        # Validate all protocol IDs
        invalid_protocols = [p for p in protocol_ids if p not in self.protocols]
        if invalid_protocols:
            return {'success': False, 'error': f'Invalid protocols: {", ".join(invalid_protocols)}'}
        
        # Check if any are already being fetched
        busy_protocols = [p for p in protocol_ids if self.is_fetching.get(p, False)]
        if busy_protocols:
            return {'success': False, 'error': f'Already fetching: {", ".join(busy_protocols)}'}
        
        print(f"Starting parallel fetch for {len(protocol_ids)} protocols: {', '.join(protocol_ids)}")
        
        # Use threading for parallel execution
        threads = []
        results = {}
        
        def thread_fetch(protocol_id):
            result = self.fetch_protocol_data(protocol_id)
            results[protocol_id] = result
        
        start_time = time.time()
        
        # Start all threads
        for protocol_id in protocol_ids:
            thread = threading.Thread(target=thread_fetch, args=(protocol_id,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_duration = time.time() - start_time
        
        # Compile results
        successful = [p for p, r in results.items() if r.get('success', False)]
        failed = [p for p, r in results.items() if not r.get('success', False)]
        
        total_count = sum(r.get('count', 0) for r in results.values() if r.get('success', False))
        
        summary = {
            'success': len(successful) > 0,
            'total_protocols': len(protocol_ids),
            'successful_protocols': len(successful),
            'failed_protocols': len(failed),
            'successful_list': successful,
            'failed_list': failed,
            'total_proposals_fetched': total_count,
            'total_duration': round(total_duration, 2),
            'results': results
        }
        
        if callback:
            callback(summary)
        
        return summary
    
    def get_fetch_status(self) -> Dict:
        """Get current fetch status for all protocols"""
        status = {
            'protocols': {},
            'currently_fetching': [],
            'total_fetching': 0
        }
        
        for protocol_id in self.protocols.keys():
            is_fetching = self.is_fetching.get(protocol_id, False)
            
            status['protocols'][protocol_id] = {
                'is_fetching': is_fetching,
                'last_fetch': self.last_fetch_times.get(protocol_id),
                'last_result': self.fetch_results.get(protocol_id, {})
            }
            
            if is_fetching:
                status['currently_fetching'].append(protocol_id)
        
        status['total_fetching'] = len(status['currently_fetching'])
        
        return status
    
    def _load_fetch_history(self):
        """Load fetch history from file"""
        history_file = "data/fetch_history.json"
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    self.last_fetch_times = history.get('last_fetch_times', {})
            except:
                self.last_fetch_times = {}
        else:
            self.last_fetch_times = {}
    
    def _save_fetch_history(self):
        """Save fetch history to file"""
        os.makedirs("data", exist_ok=True)
        history_file = "data/fetch_history.json"
        
        try:
            history = {
                'last_fetch_times': self.last_fetch_times,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving fetch history: {e}")

# Global instance
realtime_data_fetcher = RealTimeDataFetcher()