#!/bin/bash

# Check if running on Ubuntu
if ! lsb_release -a 2>/dev/null | grep -q "Ubuntu"; then
    echo "This script is designed for Ubuntu. Exiting."
    exit 1
fi

# Find all files in the current directory and subdirectories
find . -type f -not -path "./replace_core.sh" | while read -r file; do
    # Check if the file contains "...core."
    if grep -q "\.\.core\." "$file"; then
        echo "Found '...core.' in: $file"
        echo "Current matches:"
        grep --color=always "\.\.\.core\." "$file"
        echo ""
        read -p "Do you want to replace '...core.' with 'app.core.' in this file? (y/n): " answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            # Perform the replacement
            sed -i 's/\.\.\.core\./app.core./g' "$file"
            echo "Replacement done in $file"
        else
            echo "Skipping $file"
        fi
        echo ""
    fi
done

echo "Processing complete."
