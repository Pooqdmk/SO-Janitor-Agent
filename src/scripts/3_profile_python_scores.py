# src/scripts/3_profile_python_scores.py

import xml.etree.ElementTree as ET
from pathlib import Path
import re
from collections import Counter

def profile_python_scores(post_limit=10_000_000):
    """
    Processes a portion of the Posts.xml file to find all Python questions
    and analyze the distribution of their scores.
    """
    
    # --- Configuration ---
    script_location = Path(__file__).resolve().parent
    root_directory = script_location.parent.parent
    path_to_xml = root_directory / "data" / "raw" / "Posts.xml"

    # --- Pre-flight check ---
    if not path_to_xml.exists():
        print(f"❌ ERROR: Input file not found at {path_to_xml}")
        return

    print(f"🚀 Profiling scores for Python questions from the first {post_limit:,} posts...")
    
    score_counter = Counter()
    posts_processed = 0
    python_questions_found = 0

    try:
        for event, elem in ET.iterparse(str(path_to_xml), events=('end',)):
            if elem.tag == 'row':
                posts_processed += 1
                
                if posts_processed % 500_000 == 0:
                    print(f"  ...scanned {posts_processed:,} posts. Found {python_questions_found:,} Python questions.")

                if elem.get('PostTypeId') == '1':
                    tags_str = elem.get('Tags')
                    
                    if tags_str and ('<python>' in tags_str or '|python|' in tags_str):
                        python_questions_found += 1
                        score_str = elem.get('Score')
                        if score_str:
                            score = int(score_str)
                            score_counter[score] += 1
                
                elem.clear()

                if posts_processed >= post_limit:
                    print(f"\nReached post limit of {post_limit:,}. Stopping scan.")
                    break
                    
    except ET.ParseError as e:
        print(f"\n❌ An XML parsing error occurred: {e}")
        return

    print("\n" + "="*50)
    print("📊 SCORE PROFILE COMPLETE �")
    print(f"Found {python_questions_found:,} Python questions in {posts_processed:,} posts.")
    print("\nTop 20 Highest Scores and Their Counts:")
    
    # Print the most common scores, sorted from highest to lowest score
    for score, count in sorted(score_counter.items(), reverse=True)[:20]:
        print(f"  - Score: {score:<10} | Number of Questions with this score: {count:,}")

    print("\nMost Common Scores Overall:")
    for score, count in score_counter.most_common(10):
         print(f"  - Score: {score:<10} | Number of Questions with this score: {count:,}")

    print("="*50)

if __name__ == "__main__":
    profile_python_scores()
