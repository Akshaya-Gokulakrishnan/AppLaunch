#!/usr/bin/env python3
"""
System Information Application
Shows system information and monitoring
"""

import os
import sys
import time
import psutil
from datetime import datetime

def main():
    print("=== System Information Monitor ===")
    print("System monitoring for the Application Portal")
    print("=" * 50)
    
    while True:
        print("\n1. System Overview")
        print("2. CPU Information")
        print("3. Memory Information")
        print("4. Disk Information")
        print("5. Network Information")
        print("6. Running Processes")
        print("7. Real-time CPU/Memory")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            show_system_overview()
        elif choice == '2':
            show_cpu_info()
        elif choice == '3':
            show_memory_info()
        elif choice == '4':
            show_disk_info()
        elif choice == '5':
            show_network_info()
        elif choice == '6':
            show_processes()
        elif choice == '7':
            show_realtime_monitor()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def show_system_overview():
    print("\n=== System Overview ===")
    print(f"System: {os.name}")
    print(f"Platform: {sys.platform}")
    print(f"Python Version: {sys.version}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Users: {len(psutil.users())}")

def show_cpu_info():
    print("\n=== CPU Information ===")
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {psutil.cpu_count(logical=True)}")
    print(f"Current frequency: {psutil.cpu_freq().current:.2f} MHz")
    print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
    
    print("\nPer-core CPU usage:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"  Core {i}: {percentage}%")

def show_memory_info():
    print("\n=== Memory Information ===")
    memory = psutil.virtual_memory()
    print(f"Total: {get_size(memory.total)}")
    print(f"Available: {get_size(memory.available)}")
    print(f"Used: {get_size(memory.used)}")
    print(f"Percentage: {memory.percent}%")
    
    print("\nSwap Memory:")
    swap = psutil.swap_memory()
    print(f"Total: {get_size(swap.total)}")
    print(f"Free: {get_size(swap.free)}")
    print(f"Used: {get_size(swap.used)}")
    print(f"Percentage: {swap.percent}%")

def show_disk_info():
    print("\n=== Disk Information ===")
    print("Partitions and Usage:")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"Device: {partition.device}")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            print(f"  Total Size: {get_size(partition_usage.total)}")
            print(f"  Used: {get_size(partition_usage.used)}")
            print(f"  Free: {get_size(partition_usage.free)}")
            print(f"  Percentage: {partition_usage.percent}%")
        except PermissionError:
            print("  Permission denied")
        print()

def show_network_info():
    print("\n=== Network Information ===")
    print("Network interfaces:")
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            print(f"Interface: {interface_name}")
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
        print()

def show_processes():
    print("\n=== Top 10 Processes by Memory Usage ===")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
    
    print(f"{'PID':<8} {'Name':<20} {'Memory %':<10} {'CPU %':<10}")
    print("-" * 50)
    for proc in processes:
        print(f"{proc['pid']:<8} {proc['name']:<20} {proc['memory_percent']:<10.1f} {proc['cpu_percent']:<10.1f}")

def show_realtime_monitor():
    print("\n=== Real-time Monitor ===")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            print(f"\rCPU: {cpu_percent:5.1f}% | Memory: {memory_percent:5.1f}%", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

def get_size(bytes, suffix="B"):
    """Convert bytes to human readable format"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

if __name__ == "__main__":
    main()