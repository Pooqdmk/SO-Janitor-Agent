# src/scripts/2_count_all_tags.py

import xml.etree.ElementTree as ET
from pathlib import Path
import re
from collections import Counter

def profile_all_tags(post_limit=5_000_000):
    """
    Processes a portion of the Posts.xml file to count the occurrences
    of every tag, providing a profile of the most common topics.
    """
    
    # --- Configuration ---
    script_location = Path(__file__).resolve().parent
    root_directory = script_location.parent.parent
    path_to_xml = root_directory / "data" / "raw" / "Posts.xml"

    # --- Pre-flight check ---
    if not path_to_xml.exists():
        print(f"❌ ERROR: Input file not found at {path_to_xml}")
        return

    print(f"🚀 Profiling tags from the first {post_limit:,} posts...")
    
    tag_counter = Counter()
    posts_processed = 0

    try:
        for event, elem in ET.iterparse(str(path_to_xml), events=('end',)):
            if elem.tag == 'row':
                posts_processed += 1
                
                if posts_processed % 500_000 == 0:
                    print(f"  ...scanned {posts_processed:,} posts.")

                if elem.get('PostTypeId') == '1':
                    tags_str = elem.get('Tags')
                    
                    if tags_str:
                        # This regex finds all tags, whether they are in <tag> or |tag| format
                        found_tags = re.findall(r'[<|](.*?)[>|]', tags_str)
                        tag_counter.update(found_tags)
                
                elem.clear()

                if posts_processed >= post_limit:
                    print(f"\nReached post limit of {post_limit:,}. Stopping scan.")
                    break
                    
    except ET.ParseError as e:
        print(f"\n❌ An XML parsing error occurred: {e}")
        return

    print("\n" + "="*50)
    print("📊 TAG PROFILE COMPLETE 📊")
    print(f"Found {len(tag_counter):,} unique tags in {posts_processed:,} posts.")
    print("\nTop 50 Most Common Tags:")
    
    # Print the most common tags and their counts
    for tag, count in tag_counter.most_common(50):
        print(f"  - {tag:<25} | Count: {count:,}")
    print("="*50)

if __name__ == "__main__":
    profile_all_tags()
