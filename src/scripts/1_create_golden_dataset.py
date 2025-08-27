# src/scripts/1_create_golden_dataset.py

import xml.etree.ElementTree as ET
import pandas as pd
import os
from pathlib import Path
from collections import Counter
import re

def create_golden_dataset():
    """
    Parses the full Stack Overflow Posts.xml dump in two phases.
    Phase 1: Identifies the top 50 most common tags.
    Phase 2: Extracts high-quality questions belonging to those top 50 tags.
    """

    # --- Configuration ---
    script_location = Path(__file__).resolve().parent
    root_directory = script_location.parent.parent
    
    path_to_xml = root_directory / "data" / "raw" / "Posts.xml"
    output_dir = root_directory / "data" / "processed"
    output_parquet_file = output_dir / "top_50_tags_golden_questions.parquet"

    # --- Pre-flight checks ---
    if not path_to_xml.exists():
        print(f"❌ ERROR: Input file not found at {path_to_xml}")
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # --- PHASE 1: Profile all tags to find the top 50 ---
    print("🚀 Phase 1: Profiling all tags to find the top 50. This will take several hours.")
    tag_counter = Counter()
    total_posts_processed = 0
    try:
        for event, elem in ET.iterparse(str(path_to_xml), events=('end',)):
            if elem.tag == 'row':
                total_posts_processed += 1
                if total_posts_processed % 1_000_000 == 0:
                    print(f"  [Phase 1] Scanned {total_posts_processed:,} posts...")

                if elem.get('PostTypeId') == '1':
                    tags_str = elem.get('Tags')
                    if tags_str:
                        found_tags = re.findall(r'[<|](.*?)[>|]', tags_str)
                        tag_counter.update(found_tags)
                elem.clear()
    except ET.ParseError as e:
        print(f"\n❌ An XML parsing error occurred during Phase 1: {e}")
        return
    
    top_50_tags = {tag for tag, count in tag_counter.most_common(50)}
    print(f"\n✅ Phase 1 Complete. Identified Top 50 Tags.")
    print(top_50_tags)

    # --- PHASE 2: Filter for high-quality questions from the top 50 tags ---
    print("\n🚀 Phase 2: Filtering for high-quality questions. This will take several more hours.")
    questions_list = []
    total_posts_processed = 0
    final_golden_questions = 0
    try:
        for event, elem in ET.iterparse(str(path_to_xml), events=('end',)):
            if elem.tag == 'row':
                total_posts_processed += 1
                if total_posts_processed % 1_000_000 == 0:
                    print(f"  [Phase 2] Scanned {total_posts_processed:,} posts. Found {final_golden_questions:,} golden questions.")

                if elem.get('PostTypeId') == '1':
                    tags_str = elem.get('Tags')
                    if tags_str:
                        found_tags = re.findall(r'[<|](.*?)[>|]', tags_str)
                        # Check for intersection between this post's tags and our top 50 list
                        if any(tag in top_50_tags for tag in found_tags):
                            score_str = elem.get('Score')
                            accepted_answer_id = elem.get('AcceptedAnswerId')
                            if score_str and accepted_answer_id and int(score_str) > 5:
                                final_golden_questions += 1
                                questions_list.append({
                                    'Id': int(elem.get('Id')),
                                    'Title': elem.get('Title'),
                                    'Body': elem.get('Body'),
                                    'Score': int(score_str),
                                    'Tags': tags_str
                                })
                elem.clear()
    except ET.ParseError as e:
        print(f"\n❌ An XML parsing error occurred during Phase 2: {e}")
        return

    print("\n" + "="*50)
    print("📊 FINAL SUMMARY 📊")
    print(f"Total Posts Processed (each phase): {total_posts_processed:,}")
    print(f"Final Golden Questions Found:     {final_golden_questions:,}")
    print("="*50 + "\n")

    if not questions_list:
        print("No questions were found. This is unexpected.")
        return

    df = pd.DataFrame(questions_list)
    print(f"Saving the data to '{output_parquet_file}'...")
    df.to_parquet(output_parquet_file)

    file_size_mb = os.path.getsize(output_parquet_file) / (1024 * 1024)
    print(f"✅ Successfully saved the golden dataset! File size is: {file_size_mb:.2f} MB")
    print("\nHere's a sample of your new dataset:")
    print(df.head())

if __name__ == "__main__":
    create_golden_dataset()
