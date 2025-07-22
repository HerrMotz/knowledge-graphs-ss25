import pandas as pd

# Define the input and output file names
input_file = 'data.csv'
output_file = 'cleaned_data.csv'

# Load the CSV file
df = pd.read_csv(input_file)

# Define a list of allowed keywords
allowed_keywords = [
    'pizza', 'restaurant', 'pizzeria', 'bakery', 'bar', 'brewery', 'cafe', 'caf', 'breakfast', 'brunch'
]

# Define a list of keywords to exclude
exclude_keywords = [
    'strip club', 'adult', 'doctor', 'university', 'cell phone', 'repair',
    'electronics', 'equipment', 'sporting goods', 'shoe store'
]

def is_relevant_category(category):
    category_lower = str(category).lower()
    # Exclude if any forbidden keyword appears
    if any(bad_word in category_lower for bad_word in exclude_keywords):
        return False
    # Include if any of the allowed keywords appear
    return any(good_word in category_lower for good_word in allowed_keywords)

# Filter the dataframe
df_cleaned = df[df['categories'].apply(is_relevant_category)]

# Save the cleaned data to a new CSV file
df_cleaned.to_csv(output_file, index=False)

print(f"Cleaned data saved to {output_file}")
