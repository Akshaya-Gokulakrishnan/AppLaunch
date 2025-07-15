#!/usr/bin/env python3
"""
Simple Text Editor Application
A basic text editor that can be run through the portal
"""

import os
import sys
import time

def main():
    print("=== Simple Text Editor ===")
    print("A basic text editor for the Application Portal")
    print("=" * 40)
    
    while True:
        print("\n1. Create new file")
        print("2. Edit existing file")
        print("3. List files")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            create_file()
        elif choice == '2':
            edit_file()
        elif choice == '3':
            list_files()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def create_file():
    filename = input("Enter filename: ").strip()
    if not filename:
        print("Invalid filename.")
        return
    
    print(f"Creating file: {filename}")
    print("Enter your text (type 'SAVE' on a new line to save):")
    
    content = []
    while True:
        line = input()
        if line.strip() == 'SAVE':
            break
        content.append(line)
    
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(content))
        print(f"File '{filename}' saved successfully!")
    except Exception as e:
        print(f"Error saving file: {e}")

def edit_file():
    filename = input("Enter filename to edit: ").strip()
    if not filename:
        print("Invalid filename.")
        return
    
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        print(f"\nCurrent content of '{filename}':")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        print("\nEnter new content (type 'SAVE' on a new line to save):")
        new_content = []
        while True:
            line = input()
            if line.strip() == 'SAVE':
                break
            new_content.append(line)
        
        with open(filename, 'w') as f:
            f.write('\n'.join(new_content))
        print(f"File '{filename}' updated successfully!")
        
    except Exception as e:
        print(f"Error editing file: {e}")

def list_files():
    try:
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        if files:
            print("\nFiles in current directory:")
            for i, file in enumerate(files, 1):
                size = os.path.getsize(file)
                print(f"{i}. {file} ({size} bytes)")
        else:
            print("No files found in current directory.")
    except Exception as e:
        print(f"Error listing files: {e}")

if __name__ == "__main__":
    main()