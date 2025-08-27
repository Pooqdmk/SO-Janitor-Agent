import pandas as pd

# Define the path to your new file
file_path = "data/processed/top_50_tags_golden_questions.parquet"

# Read the Parquet file into a pandas DataFrame
print(f"Loading data from {file_path}...")
df = pd.read_parquet(file_path)
print("...Data loaded successfully!")

# --- Now you can inspect your data ---

# Print the first 5 rows to see what it looks like
print("\nFirst 5 rows of the dataset:")
print(df.head())

# Print information about the columns and memory usage
print("\nDataset Info:")
df.info()

# Print the total number of questions
print(f"\nTotal number of questions in the file: {len(df):,}")