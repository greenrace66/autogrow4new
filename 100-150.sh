#!/bin/bash

# Directory to search
search_dir="100-150/"

# Temporary file to store output
temp_file=$(mktemp)

# Find all files ending with .pdbqt_docking_output.txt recursively in the specified directory
find "$search_dir" -type f -name "*.pdbqt_docking_output.txt" | while read -r file
do
  # Check if the file has at least 40 lines
  if [ $(wc -l < "$file") -ge 40 ]; then
    # Get the 40th line
    line=$(sed -n '40p' "$file")
    # Output the file name and the 40th line to the temporary file
    echo "$line $file" >> "$temp_file"
  else
    echo "$file does not have 40 lines."
  fi
done

# Sort the temporary file in descending order of the first column (numeric sort) and print
sort -nr "$temp_file"

# Remove the temporary file
rm "$temp_file"
