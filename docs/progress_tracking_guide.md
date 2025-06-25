# Progress Tracking Guide

This guide explains how to monitor and track the progress of your x-pull-request-reviewer training process in real-time.

## 🎯 Why Progress Tracking?

Training a model can take 30-60 minutes, and it's important to know:
- **Is the system working or hung?**
- **What step is currently running?**
- **How much time is left?**
- **Are there any issues?**

## 📊 Progress Tracking Features

### **Real-Time Progress Display**
- ✅ **Step-by-step progress** with timestamps
- ✅ **Resource monitoring** (memory, disk, CPU)
- ✅ **File creation tracking** (logs, datasets, models)
- ✅ **Time estimates** for each step
- ✅ **Success/failure indicators** for each step

### **Multiple Monitoring Options**
- ✅ **Integrated progress** in training script
- ✅ **Separate monitoring** in another terminal
- ✅ **Quick status checks** without continuous monitoring
- ✅ **Detailed logs** for troubleshooting

## 🚀 How to Use Progress Tracking

### **Option 1: Integrated Progress (Recommended)**

The training script now includes built-in progress tracking:

```bash
# Run training with progress tracking
python scripts/safe_training.py
```

**What you'll see:**
```
============================================================
🚀 X-PULL-REQUEST-REVIEWER SAFE TRAINING
============================================================
📋 Training plan: 6 steps
🔧 Technologies: go, python
💾 System: 8GB RAM, 8.0GB available
============================================================

[11:30:15] 🔄 System resource check
[11:30:16] ✅ System resource check (1.2s)

[11:30:16] 🔄 Creating backup of existing model
[11:30:16]   📝 Checking for existing codellama model (0.1s)
[11:30:16]   📝 Creating backup directory: model_backups/codellama_backup_20240624_113016 (0.1s)
[11:30:18]   📝 Copying model files (this may take a few minutes) (2.1s)
[11:30:18] ✅ Creating backup of existing model (2.3s)

[11:30:18] 🔄 Scraping go documentation
[11:30:18]   📝 Starting scraper: python xprr_agent.py scrape-docs --technology go --max-pages 15 --delay 3.0 (0.1s)
[11:30:48]   📝 Scraping in progress... (checking resources) (30.2s)
[11:30:58]   📝 Successfully scraped 15 pages (40.1s)
[11:30:58] ✅ Scraping go documentation (40.2s)
```

### **Option 2: Separate Monitoring Terminal**

Run the monitoring script in a separate terminal:

```bash
# Terminal 1: Start training
python scripts/safe_training.py

# Terminal 2: Monitor progress
python scripts/monitor_training.py
```

**What you'll see in the monitor:**
```
🔍 X-PULL-REQUEST-REVIEWER TRAINING MONITOR
==================================================
📅 Monitoring Time: 2024-06-24 11:30:15
==================================================
💻 SYSTEM RESOURCES:
   Memory: 65.2% used (2.8GB available)
   Disk: 64.0% used (8.0GB available)
   CPU: 45.3%

📁 TRAINING FILES:
   ✅ training.log: 2.3KB (modified: 11:30:18)
   ❌ training_report.md: Not found
   ❌ Modelfile: Not found
   ❌ training_dataset.jsonl: Not found
   ✅ model_backups: 1 items

🤖 OLLAMA MODELS:
   📦 codellama:latest: 3.8 GB (ID: 8fdf8f75...)
   📦 codellama:7b-instruct: 3.8 GB (ID: 8fdf8f75...)

📝 RECENT TRAINING LOG:
   [11:30:15] INFO - Starting safe training process
   [11:30:16] INFO - System healthy - Memory: 65.2%, Disk: 64.0%, CPU: 45.3%
   [11:30:16] INFO - Creating backup of existing model
   [11:30:18] INFO - Model backup created at: model_backups/codellama_backup_20240624_113016
   [11:30:18] INFO - Starting documentation scraping for go

🎯 PROGRESS INDICATORS:
   🔄 Training script is running
      PID: 12345
   📝 Recent activity: training.log
```

### **Option 3: Quick Status Check**

For a quick overview without continuous monitoring:

```bash
python scripts/monitor_training.py --quick
```

**What you'll see:**
```
🔍 QUICK TRAINING STATUS
==============================
Memory: 65.2% used
Disk: 8.0GB available
Training log: ✅
Training dataset: ❌
Modelfile: ❌
Trained models: 0
```

## 📋 Understanding Progress Indicators

### **Step Status Icons**
- 🔄 **Running**: Step is currently in progress
- ✅ **Success**: Step completed successfully
- ❌ **Failed**: Step failed (check logs for details)
- 📝 **Substep**: Detailed progress within a step

### **Resource Indicators**
- 🟢 **Green**: Resources are healthy
- 🟡 **Yellow**: Resources are getting low
- 🔴 **Red**: Resources are critical (training may stop)

### **File Status**
- ✅ **Found**: File exists and is being updated
- ❌ **Not found**: File doesn't exist yet
- 📊 **Size shown**: File size indicates progress

## 🔍 What Each Step Does

### **1. System Resource Check**
- Checks memory, disk, and CPU usage
- Ensures system can handle training
- **Time**: 1-2 seconds

### **2. Backup Existing Model**
- Creates timestamped backup of your current model
- Copies all model files to `model_backups/`
- **Time**: 2-5 minutes (depends on model size)

### **3. Scrape Documentation**
- Downloads official documentation from websites
- Processes content into training format
- **Time**: 10-30 minutes per technology
- **Progress**: Shows pages scraped and resource checks

### **4. Create Training Dataset**
- Converts scraped data into training format
- Creates JSONL file for fine-tuning
- **Time**: 1-5 minutes
- **Progress**: Shows number of training examples created

### **5. Create Modelfile**
- Generates configuration for fine-tuning
- Sets up parameters optimized for your system
- **Time**: 1-2 seconds

### **6. Fine-tune Model**
- Trains the model on your documentation
- Creates new model with timestamp
- **Time**: 15-45 minutes (depends on data size)
- **Progress**: Shows elapsed time and resource monitoring

### **7. Generate Training Report**
- Creates summary of training process
- Saves report to `training_report.md`
- **Time**: 1-2 seconds

## 🚨 Troubleshooting Progress Issues

### **Issue: "Training seems stuck"**

**Check these indicators:**
1. **Resource usage**: Is memory/CPU high?
2. **File activity**: Are files being updated?
3. **Process status**: Is the training script running?

**Solutions:**
```bash
# Check if training is running
ps aux | grep safe_training.py

# Check recent log activity
tail -f training.log

# Check system resources
top -l 1 | head -10
```

### **Issue: "Step failed"**

**Check the logs:**
```bash
# View detailed error logs
cat training.log | grep ERROR

# Check specific step logs
cat training.log | grep "Scraping go documentation"
```

**Common failures:**
- **Network issues**: Documentation scraping fails
- **Disk space**: Not enough space for backup
- **Memory**: System runs out of memory
- **Ollama issues**: Model creation fails

### **Issue: "Progress not updating"**

**Check monitoring:**
```bash
# Restart monitoring
python scripts/monitor_training.py

# Check file timestamps
ls -la training_data/
ls -la model_backups/
```

## 📊 Progress Tracking Best Practices

### **Before Starting Training**
1. **Close unnecessary applications** to free memory
2. **Check disk space** (need 5GB+ available)
3. **Ensure stable internet** for documentation scraping
4. **Keep system plugged in** (if laptop)

### **During Training**
1. **Keep monitoring terminal open** to watch progress
2. **Don't run other heavy applications**
3. **Check logs if progress seems stuck**
4. **Be patient** - some steps take longer than others

### **After Training**
1. **Verify new model exists**: `ollama list`
2. **Test the model**: Try a sample code review
3. **Keep backup**: Original model is preserved
4. **Check training report**: Review results

## 🔧 Advanced Monitoring

### **Custom Monitoring Scripts**

You can create custom monitoring scripts:

```python
#!/usr/bin/env python3
# custom_monitor.py

import time
import os
from datetime import datetime

def check_training_progress():
    """Custom progress check."""
    files = ['training.log', 'training_dataset.jsonl', 'Modelfile']
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            modified = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"✅ {file}: {size} bytes, modified: {modified}")
        else:
            print(f"❌ {file}: Not found")

if __name__ == "__main__":
    while True:
        print(f"\n--- {datetime.now()} ---")
        check_training_progress()
        time.sleep(30)
```

### **Integration with CI/CD**

For automated environments:

```bash
# Check training status in CI/CD
python scripts/monitor_training.py --quick

# Exit with error if training failed
if [ $? -ne 0 ]; then
    echo "Training failed"
    exit 1
fi
```

## 📈 Progress Metrics

### **Expected Timings (8GB RAM)**
- **System check**: 1-2 seconds
- **Backup**: 2-5 minutes
- **Scraping (per tech)**: 10-30 minutes
- **Dataset creation**: 1-5 minutes
- **Fine-tuning**: 15-45 minutes
- **Total time**: 30-90 minutes

### **Resource Usage Patterns**
- **Memory**: Peaks during fine-tuning (6-7GB)
- **Disk**: Grows with scraped data and models
- **CPU**: High during scraping and fine-tuning
- **Network**: Active during documentation scraping

### **Success Indicators**
- ✅ All steps complete without errors
- ✅ New model appears in `ollama list`
- ✅ Training report generated
- ✅ System resources remain stable
- ✅ Original model preserved in backup

## 🎉 Completion Checklist

When training completes successfully, you should have:

- ✅ **New trained model**: `codellama-trained-YYYYMMDD_HHMMSS`
- ✅ **Backup of original**: In `model_backups/`
- ✅ **Training dataset**: `training_data/training_dataset.jsonl`
- ✅ **Training report**: `training_report.md`
- ✅ **Detailed logs**: `training.log`

**Next steps:**
1. Test the new model: `ollama run codellama-trained-YYYYMMDD_HHMMSS`
2. Update configuration to use new model
3. Start reviewing code with enhanced knowledge

---

**With this progress tracking system, you'll always know exactly what's happening during training!** 🚀 