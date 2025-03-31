#!/usr/bin/env python
"""
Script to fix imports in the Tropical Vending project.
Replaces 'backend.core' with 'core' in all Python files.
"""

import os
import re
from pathlib import Path

def fix_imports(directory):
    """Recursively find and fix imports in Python files"""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace imports
                new_content = re.sub(r'from backend\.core', 'from core', content)
                new_content = re.sub(r'import backend\.core', 'import core', new_content)
                
                # Write back if changes were made
                if new_content != content:
                    print(f"Fixing imports in {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1
    
    return count

if __name__ == "__main__":
    # Start from the backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("Backend directory not found!")
        exit(1)
    
    # Fix imports
    count = fix_imports(backend_dir)
    print(f"Fixed imports in {count} files.") 