#!/usr/bin/env python3
"""
Fetch all TRON TIPs from GitHub
"""
import requests
import json
import re
from datetime import datetime
import sys

def fetch_all_tron_tips():
    """Fetch ALL TRON TIPs from GitHub"""
    try:
        print("Fetching TRON TIPs from GitHub...")
        
        # Get list of TIP files
        url = 'https://api.github.com/repos/tronprotocol/tips/contents'
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f'Failed to get file list: {response.status_code}')
            return None
            
        files = response.json()
        tip_files = [f for f in files if f['name'].startswith('tip-') and f['name'].endswith('.md')]
        
        print(f'Found {len(tip_files)} TIP files total')
        print('Processing all TIPs...')
        
        tips = []
        
        # Process ALL TIPs
        for i, tip_file in enumerate(tip_files, 1):
            try:
                if i % 10 == 0:
                    print(f'Processed {i}/{len(tip_files)} TIPs...')
                
                # Extract TIP number from filename
                tip_num = re.search(r'tip-(\d+)', tip_file['name'])
                if not tip_num:
                    continue
                    
                tip_number = int(tip_num.group(1))
                
                # Get file content
                content_response = requests.get(tip_file['download_url'], timeout=10)
                if content_response.status_code != 200:
                    continue
                    
                content = content_response.text
                
                # Parse markdown content for metadata
                title_match = re.search(r'title:\s*(.+)', content, re.MULTILINE | re.IGNORECASE)
                if not title_match:
                    title_match = re.search(r'^#\s*TIP[-\s]*\d*:?\s*(.+)', content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else f'TIP {tip_number}'
                
                author_match = re.search(r'author:\s*(.+)', content, re.MULTILINE | re.IGNORECASE)
                author = author_match.group(1).strip() if author_match else 'Unknown'
                
                status_match = re.search(r'status:\s*(.+)', content, re.MULTILINE | re.IGNORECASE)
                status = status_match.group(1).strip() if status_match else 'Draft'
                
                type_match = re.search(r'type:\s*(.+)', content, re.MULTILINE | re.IGNORECASE)
                tip_type = type_match.group(1).strip() if type_match else 'Standards Track'
                
                created_match = re.search(r'created:\s*(.+)', content, re.MULTILINE | re.IGNORECASE)
                created = created_match.group(1).strip() if created_match else '2018-01-01'
                
                # Create TIP object
                tip = {
                    'number': tip_number,
                    'id': f'TIP-{tip_number}',
                    'title': title[:100],
                    'author': author[:100],
                    'type': tip_type,
                    'category': 'Protocol',
                    'status': status,
                    'created': created,
                    'url': f'https://github.com/tronprotocol/tips/blob/master/{tip_file["name"]}',
                    'file_url': tip_file['download_url'],
                    'protocol': 'tron',
                    'summary': content[:300] + '...',
                    'source': 'https://github.com/tronprotocol/tips'
                }
                
                tips.append(tip)
                
            except Exception as e:
                print(f'Error processing {tip_file["name"]}: {e}')
                continue
        
        return tips
        
    except Exception as e:
        print(f'Fatal error fetching TIPs: {e}')
        return None

def main():
    # Fetch ALL TIPs
    tips = fetch_all_tron_tips()

    if tips:
        # Save to file
        tips_data = {
            'generated_at': int(datetime.now().timestamp()),
            'generated_at_iso': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'count': len(tips),
            'protocol': 'tron',
            'source': 'https://github.com/tronprotocol/tips',
            'items': tips
        }
        
        with open('data/tips.json', 'w', encoding='utf-8') as f:
            json.dump(tips_data, f, indent=2, ensure_ascii=False)
        
        print(f'\n✅ SUCCESS! Fetched and saved {len(tips)} TIPs total!')
        
        # Show some statistics
        statuses = {}
        types = {}
        years = {}
        
        for tip in tips:
            status = tip.get('status', 'Unknown')
            tip_type = tip.get('type', 'Unknown')
            created = tip.get('created', '2018')
            year = created[:4] if len(created) >= 4 else '2018'
            
            statuses[status] = statuses.get(status, 0) + 1
            types[tip_type] = types.get(tip_type, 0) + 1
            years[year] = years.get(year, 0) + 1
        
        print(f'\n📊 TIP Statistics:')
        print(f'Total TIPs: {len(tips)}')
        print(f'Status breakdown: {dict(statuses)}')
        print(f'Type breakdown: {dict(types)}')
        print(f'Year breakdown: {dict(sorted(years.items()))}')
        
        # Show recent TIPs
        recent_tips = [tip for tip in tips if '2024' in tip.get('created', '') or '2025' in tip.get('created', '')]
        print(f'\n🆕 Recent TIPs ({len(recent_tips)} found):')
        for tip in recent_tips[:5]:
            print(f'  {tip["id"]}: {tip["title"]} ({tip["created"]})')
            
    else:
        print('❌ Failed to fetch TIPs')

if __name__ == "__main__":
    main()