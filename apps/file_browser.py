#!/usr/bin/env python3
"""
File Browser Application
A simple file browser that can be run through the portal
"""

import os
import sys
import time
from datetime import datetime

def main():
    print("=== File Browser ===")
    print("A simple file browser for the Application Portal")
    print("=" * 40)
    
    current_dir = os.getcwd()
    
    while True:
        print(f"\nCurrent directory: {current_dir}")
        print("\n1. List files and directories")
        print("2. Change directory")
        print("3. View file content")
        print("4. File information")
        print("5. Go to parent directory")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            list_directory(current_dir)
        elif choice == '2':
            new_dir = change_directory(current_dir)
            if new_dir:
                current_dir = new_dir
        elif choice == '3':
            view_file(current_dir)
        elif choice == '4':
            show_file_info(current_dir)
        elif choice == '5':
            parent_dir = os.path.dirname(current_dir)
            if parent_dir != current_dir:
                current_dir = parent_dir
                print(f"Changed to: {current_dir}")
            else:
                print("Already at root directory.")
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def list_directory(path):
    try:
        items = os.listdir(path)
        if not items:
            print("Directory is empty.")
            return
        
        print(f"\nContents of {path}:")
        print("-" * 60)
        print(f"{'Name':<25} {'Type':<10} {'Size':<10} {'Modified'}")
        print("-" * 60)
        
        for item in sorted(items):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                item_type = "Directory"
                size = "-"
            else:
                item_type = "File"
                size = f"{os.path.getsize(item_path)} bytes"
            
            modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M')
            print(f"{item:<25} {item_type:<10} {size:<10} {modified}")
            
    except Exception as e:
        print(f"Error listing directory: {e}")

def change_directory(current_dir):
    dirname = input("Enter directory name: ").strip()
    if not dirname:
        print("Invalid directory name.")
        return None
    
    new_path = os.path.join(current_dir, dirname)
    
    if os.path.exists(new_path) and os.path.isdir(new_path):
        print(f"Changed to: {new_path}")
        return new_path
    else:
        print(f"Directory '{dirname}' not found.")
        return None

def view_file(current_dir):
    filename = input("Enter filename to view: ").strip()
    if not filename:
        print("Invalid filename.")
        return
    
    filepath = os.path.join(current_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"File '{filename}' not found.")
        return
    
    if os.path.isdir(filepath):
        print(f"'{filename}' is a directory, not a file.")
        return
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        print(f"\nContent of '{filename}':")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
    except Exception as e:
        print(f"Error reading file: {e}")

def show_file_info(current_dir):
    filename = input("Enter filename for info: ").strip()
    if not filename:
        print("Invalid filename.")
        return
    
    filepath = os.path.join(current_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"File '{filename}' not found.")
        return
    
    try:
        stat = os.stat(filepath)
        print(f"\nFile Information for '{filename}':")
        print("-" * 30)
        print(f"Full path: {filepath}")
        print(f"Size: {stat.st_size} bytes")
        print(f"Created: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Type: {'Directory' if os.path.isdir(filepath) else 'File'}")
        print(f"Permissions: {oct(stat.st_mode)[-3:]}")
        
    except Exception as e:
        print(f"Error getting file info: {e}")

if __name__ == "__main__":
    main()