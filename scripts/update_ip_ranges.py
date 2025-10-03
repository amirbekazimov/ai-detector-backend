#!/usr/bin/env python3
"""Script to update AI bot IP ranges from external sources."""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

from app.db.session import SessionLocal
from app.services.ip_range_service import IPRangeService


async def main():
    """Main function to update IP ranges."""
    print("🤖 Starting AI Bot IP Ranges Update...")
    
    db = SessionLocal()
    try:
        ip_service = IPRangeService(db)
        
        print("📡 Updating IP ranges from all sources...")
        result = await ip_service.update_all_ai_bot_ips()
        
        print(f"✅ Update completed!")
        print(f"📊 Sources processed: {result['total_sources']}")
        print(f"✅ Successful updates: {result['successful_updates']}")
        print(f"❌ Failed updates: {result['failed_updates']}")
        
        for source_name, source_result in result['sources'].items():
            if source_result['success']:
                print(f"  ✅ {source_name}: {source_result['total_ips']} IPs ({source_result['new_ips_count']} new)")
            else:
                print(f"  ❌ {source_name}: {source_result.get('error', 'Unknown error')}")
        
        # Show current stats
        stats = ip_service.get_bot_ip_stats()
        print(f"\n📈 Current IP Range Statistics:")
        print(f"  Total IP ranges: {stats['total_ip_ranges']}")
        print(f"  Active IP ranges: {stats['active_ip_ranges']}")
        print(f"  Inactive IP ranges: {stats['inactive_ip_ranges']}")
        
        if stats['bot_statistics']:
            print(f"\n🤖 Bot Statistics:")
            for bot_name, count in stats['bot_statistics'].items():
                print(f"  {bot_name}: {count} IPs")
        
    except Exception as e:
        print(f"❌ Error during update: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
