#!/usr/bin/env python3
"""
Training Progress Monitor
Run this in a separate terminal to monitor training progress in real-time.
"""

import os
import time
import psutil
import subprocess
from datetime import datetime
from pathlib import Path

def get_system_resources():
    """Get current system resource usage."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return {
        'memory_used_percent': memory.percent,
        'memory_available_gb': memory.available / (1024**3),
        'disk_used_percent': disk.percent,
        'disk_available_gb': disk.free / (1024**3),
        'cpu_percent': cpu_percent
    }

def check_training_files():
    """Check for training-related files and their status."""
    files = {
        'training.log': 'training.log',
        'training_report.md': 'training_report.md',
        'Modelfile': 'Modelfile',
        'training_dataset.jsonl': 'training_data/training_dataset.jsonl',
        'model_backups': 'model_backups/'
    }
    
    status = {}
    for name, path in files.items():
        if os.path.exists(path):
            if os.path.isfile(path):
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path))
                status[name] = {
                    'exists': True,
                    'size': size,
                    'modified': modified,
                    'type': 'file'
                }
            else:
                # Directory
                items = len(os.listdir(path)) if os.path.exists(path) else 0
                status[name] = {
                    'exists': True,
                    'items': items,
                    'type': 'directory'
                }
        else:
            status[name] = {'exists': False}
    
    return status

def check_ollama_models():
    """Check current Ollama models."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            models = []
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        models.append({
                            'name': parts[0],
                            'id': parts[1],
                            'size': parts[2],
                            'modified': ' '.join(parts[3:]) if len(parts) > 3 else ''
                        })
            return models
        else:
            return []
    except:
        return []

def format_size(size_bytes):
    """Format bytes to human readable size."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def monitor_training():
    """Main monitoring function."""
    print("🔍 X-PULL-REQUEST-REVIEWER TRAINING MONITOR")
    print("=" * 50)
    print("Press Ctrl+C to stop monitoring")
    print("=" * 50)
    
    try:
        while True:
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Get current time
            now = datetime.now()
            print(f"📅 Monitoring Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            
            # System Resources
            resources = get_system_resources()
            print("💻 SYSTEM RESOURCES:")
            print(f"   Memory: {resources['memory_used_percent']:.1f}% used ({resources['memory_available_gb']:.1f}GB available)")
            print(f"   Disk: {resources['disk_used_percent']:.1f}% used ({resources['disk_available_gb']:.1f}GB available)")
            print(f"   CPU: {resources['cpu_percent']:.1f}%")
            
            # Training Files Status
            print("\n📁 TRAINING FILES:")
            files = check_training_files()
            for name, info in files.items():
                if info['exists']:
                    if info['type'] == 'file':
                        size_str = format_size(info['size'])
                        modified = info['modified'].strftime('%H:%M:%S')
                        print(f"   ✅ {name}: {size_str} (modified: {modified})")
                    else:
                        items = info['items']
                        print(f"   ✅ {name}: {items} items")
                else:
                    print(f"   ❌ {name}: Not found")
            
            # Ollama Models
            print("\n🤖 OLLAMA MODELS:")
            models = check_ollama_models()
            if models:
                for model in models:
                    print(f"   📦 {model['name']}: {model['size']} (ID: {model['id'][:8]}...)")
            else:
                print("   ❌ No models found or Ollama not running")
            
            # Training Log (last few lines)
            print("\n📝 RECENT TRAINING LOG:")
            if os.path.exists('training.log'):
                try:
                    with open('training.log', 'r') as f:
                        lines = f.readlines()
                        # Show last 5 lines
                        for line in lines[-5:]:
                            line = line.strip()
                            if line:
                                # Extract timestamp and message
                                if ' - ' in line:
                                    parts = line.split(' - ', 2)
                                    if len(parts) >= 3:
                                        timestamp = parts[0]
                                        level = parts[1]
                                        message = parts[2]
                                        print(f"   [{timestamp}] {message}")
                                    else:
                                        print(f"   {line}")
                                else:
                                    print(f"   {line}")
                except:
                    print("   ❌ Error reading training log")
            else:
                print("   ❌ training.log not found")
            
            # Progress Indicators
            print("\n🎯 PROGRESS INDICATORS:")
            
            # Check if training is actively running
            training_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'safe_training.py' in cmdline:
                            training_processes.append(proc.info)
                except:
                    pass
            
            if training_processes:
                print("   🔄 Training script is running")
                for proc in training_processes:
                    print(f"      PID: {proc['pid']}")
            else:
                print("   ⏸️  Training script not running")
            
            # Check for recent activity
            recent_files = []
            for name, info in files.items():
                if info['exists'] and info['type'] == 'file':
                    if (now - info['modified']).total_seconds() < 300:  # 5 minutes
                        recent_files.append(name)
            
            if recent_files:
                print(f"   📝 Recent activity: {', '.join(recent_files)}")
            else:
                print("   💤 No recent file activity")
            
            print("\n" + "=" * 50)
            print("Monitoring will refresh every 10 seconds...")
            print("Press Ctrl+C to stop")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
        print("Training may still be running in the background")

def quick_status():
    """Quick status check without continuous monitoring."""
    print("🔍 QUICK TRAINING STATUS")
    print("=" * 30)
    
    # System resources
    resources = get_system_resources()
    print(f"Memory: {resources['memory_used_percent']:.1f}% used")
    print(f"Disk: {resources['disk_available_gb']:.1f}GB available")
    
    # Training files
    files = check_training_files()
    training_log_exists = files.get('training.log', {}).get('exists', False)
    dataset_exists = files.get('training_dataset.jsonl', {}).get('exists', False)
    modelfile_exists = files.get('Modelfile', {}).get('exists', False)
    
    print(f"Training log: {'✅' if training_log_exists else '❌'}")
    print(f"Training dataset: {'✅' if dataset_exists else '❌'}")
    print(f"Modelfile: {'✅' if modelfile_exists else '❌'}")
    
    # Models
    models = check_ollama_models()
    trained_models = [m for m in models if 'trained' in m['name']]
    print(f"Trained models: {len(trained_models)}")
    
    if trained_models:
        for model in trained_models:
            print(f"  - {model['name']} ({model['size']})")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_status()
    else:
        monitor_training() 