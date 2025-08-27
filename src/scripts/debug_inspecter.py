# src/scripts/debug_xml_inspector.py

import xml.etree.ElementTree as ET
from pathlib import Path

def inspect_first_posts(limit=10):
    """
    Reads and prints the attributes of the first few 'row' elements
    from the Posts.xml file to help with debugging.
    """
    
    # --- Configuration ---
    script_location = Path(__file__).resolve().parent
    root_directory = script_location.parent.parent
    path_to_xml = root_directory / "data" / "raw" / "Posts.xml"

    # --- Pre-flight check ---
    if not path_to_xml.exists():
        print(f"❌ ERROR: Input file not found at {path_to_xml}")
        return

    print(f"🔍 Inspecting the first {limit} posts in {path_to_xml}...\n")

    post_count = 0
    
    try:
        # Use iterparse to read the file incrementally
        for event, elem in ET.iterparse(str(path_to_xml), events=('end',)):
            if elem.tag == 'row':
                print("-" * 50)
                print(f"Post #{post_count + 1}")
                
                # Print all attributes for the current row
                print("Attributes found:")
                for key, value in elem.attrib.items():
                    print(f"  - {key}: {value}")
                
                post_count += 1
                
                # Stop after reaching the limit
                if post_count >= limit:
                    break
                
                elem.clear() # Free up memory
            
    except ET.ParseError as e:
        print(f"\n❌ An XML parsing error occurred: {e}")

    print("\n" + "="*50)
    print("Inspection complete.")
    print("Please check the attribute names (e.g., 'PostTypeId', 'Tags', 'Score') and their values.")
    print("They must exactly match what the filtering script expects.")


if __name__ == "__main__":
    # Let's look at the first 10 posts to start
    inspect_first_posts(limit=10)
