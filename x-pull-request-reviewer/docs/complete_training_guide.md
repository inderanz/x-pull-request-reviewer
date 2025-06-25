# Complete Training Guide: End-to-End Model Training

This guide provides a complete, safe process for training your x-pull-request-reviewer model on official documentation while preserving your existing model.

## 🛡️ Safety First: What This Guide Protects

### **Your Existing Model**
- ✅ **Automatic Backup**: Creates timestamped backups before any changes
- ✅ **Resource Monitoring**: Prevents system overload during training
- ✅ **Rollback Capability**: Original model is never modified
- ✅ **Conservative Settings**: Optimized for 8GB RAM systems

### **Your System**
- ✅ **Memory Monitoring**: Stops if memory usage exceeds 85%
- ✅ **Disk Space Check**: Ensures 5GB+ available space
- ✅ **CPU Monitoring**: Prevents system lockup
- ✅ **Graceful Termination**: Safe shutdown if resources are low

## 🚀 Quick Start (Recommended)

### **Step 1: Run Safe Training Script**
```bash
# Make script executable
chmod +x scripts/safe_training.py

# Run the safe training process
python scripts/safe_training.py
```

The script will:
1. Check your system resources
2. Create a backup of your existing model
3. Scrape documentation for selected technologies
4. Create training datasets
5. Fine-tune your model safely
6. Generate a training report

### **Step 2: Follow Interactive Prompts**
```
=== X-PULL-REQUEST-REVIEWER SAFE TRAINING ===
This will train your model on official documentation
System will be monitored throughout the process

Available technologies: go, java, python, terraform, kubernetes, helm, fluxcd, argocd
Recommended to start with 1-2 technologies for 8GB RAM

Enter technologies to train (comma-separated, e.g., 'go,python'): go,python
```

## 📋 Detailed Step-by-Step Process

### **Phase 1: System Preparation**

#### 1.1 Check System Requirements
```bash
# Verify system resources
python scripts/safe_training.py
```

**Requirements:**
- **Memory**: 8GB RAM (minimum)
- **Storage**: 5GB+ available space
- **CPU**: 8 cores (adequate)
- **Network**: Stable internet connection

#### 1.2 Close Unnecessary Applications
```bash
# Check current memory usage
top -l 1 | head -10

# Close memory-intensive applications:
# - Web browsers with many tabs
# - Video editing software
# - Virtual machines
# - Other AI/ML processes
```

### **Phase 2: Model Backup**

#### 2.1 Automatic Backup Creation
The safe training script automatically:
- Creates timestamped backup: `model_backups/codellama_backup_YYYYMMDD_HHMMSS/`
- Copies all model files from `~/.ollama/models/`
- Verifies backup integrity

#### 2.2 Manual Backup (Optional)
```bash
# Create manual backup
mkdir -p model_backups/manual_backup_$(date +%Y%m%d_%H%M%S)
cp -r ~/.ollama/models/* model_backups/manual_backup_$(date +%Y%m%d_%H%M%S)/
```

### **Phase 3: Documentation Scraping**

#### 3.1 Conservative Scraping
```bash
# Scrape with resource monitoring
python xprr_agent.py scrape-docs --technology go --max-pages 15 --delay 3.0
python xprr_agent.py scrape-docs --technology python --max-pages 15 --delay 3.0
```

**Conservative Settings for 8GB RAM:**
- **Max Pages**: 15 per technology (reduces memory usage)
- **Delay**: 3.0 seconds (respects rate limits)
- **Monitoring**: Automatic resource checks every 10 seconds

#### 3.2 Verify Scraped Data
```bash
# Check scraped data
ls -la training_data/
cat training_data/go_docs.json | jq '.total_pages'
```

### **Phase 4: Training Dataset Creation**

#### 4.1 Generate Training Data
```bash
# Create training dataset
python xprr_agent.py create-dataset

# Verify dataset
wc -l training_data/training_dataset.jsonl
head -1 training_data/training_dataset.jsonl | python -m json.tool
```

#### 4.2 Dataset Quality Check
```bash
# Count training examples
python -c "
import json
count = sum(1 for line in open('training_data/training_dataset.jsonl'))
print(f'Training examples: {count}')
if count < 10:
    print('⚠️  Very few examples - consider scraping more data')
elif count > 100:
    print('✅ Good number of examples')
"
```

### **Phase 5: Model Fine-tuning**

#### 5.1 Automatic Fine-tuning
The safe training script automatically:
- Creates a Modelfile with conservative parameters
- Runs fine-tuning with resource monitoring
- Creates a new model: `codellama-trained-YYYYMMDD_HHMMSS`

#### 5.2 Manual Fine-tuning (Alternative)
```bash
# Create Modelfile
cat > Modelfile << 'EOF'
FROM codellama:7b-instruct

SYSTEM "You are a senior DevOps engineer trained on official documentation."

TEMPLATE "{{ .Prompt }}"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 4096

TRAINING training_data/training_dataset.jsonl
EOF

# Create fine-tuned model
ollama create codellama-trained-manual -f Modelfile
```

### **Phase 6: Verification and Testing**

#### 6.1 Verify New Model
```bash
# List all models
ollama list

# Test the new model
ollama run codellama-trained-YYYYMMDD_HHMMSS "Review this Go code: package main; func main() { fmt.Println('Hello') }"
```

#### 6.2 Update Configuration
```bash
# Edit config to use new model
vim config/default.yaml
```

Update the model name:
```yaml
llm:
  provider: ollama
  model: codellama-trained-YYYYMMDD_HHMMSS  # Your new model
  port: 11434
```

## 🔧 Advanced Configuration

### **Resource Monitoring Settings**
Edit `scripts/safe_training.py` to adjust thresholds:
```python
# Resource thresholds
self.memory_threshold = 0.85  # 85% memory usage
self.disk_threshold = 0.90    # 90% disk usage
self.cpu_threshold = 0.95     # 95% CPU usage
```

### **Training Parameters**
Adjust Modelfile parameters for your system:
```bash
# For more conservative training (8GB RAM)
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 4096

# For more aggressive training (16GB+ RAM)
PARAMETER temperature 0.8
PARAMETER top_p 0.95
PARAMETER top_k 50
PARAMETER repeat_penalty 1.05
PARAMETER num_ctx 8192
```

### **Scraping Configuration**
```bash
# Conservative scraping (8GB RAM)
python xprr_agent.py scrape-docs --technology go --max-pages 10 --delay 5.0

# Aggressive scraping (16GB+ RAM)
python xprr_agent.py scrape-docs --technology go --max-pages 50 --delay 2.0
```

## 📊 Monitoring and Troubleshooting

### **Resource Monitoring**
The training script logs resource usage to `training.log`:
```bash
# Monitor training progress
tail -f training.log

# Check resource usage
grep "System healthy" training.log
grep "Memory usage high" training.log
```

### **Common Issues and Solutions**

#### **Issue: "Memory usage high"**
```bash
# Solution: Close applications and restart
# - Close web browsers
# - Stop other AI processes
# - Restart training with fewer technologies
```

#### **Issue: "Low disk space"**
```bash
# Solution: Free up space
# - Remove old model backups
# - Clear temporary files
# - Delete unused applications
```

#### **Issue: "Fine-tuning failed"**
```bash
# Solution: Check logs and retry
# - Check training.log for errors
# - Verify training dataset exists
# - Try with smaller dataset
```

### **Recovery Procedures**

#### **Restore Original Model**
```bash
# If training fails, restore from backup
ollama rm codellama-trained-YYYYMMDD_HHMMSS  # Remove failed model
# Original model is preserved in backups/
```

#### **Clean Up Failed Training**
```bash
# Remove failed training artifacts
rm -rf training_data/*_docs.json
rm -f Modelfile
rm -f training.log
```

## 🎯 Best Practices

### **For 8GB RAM Systems**
1. **Start Small**: Train on 1-2 technologies first
2. **Monitor Resources**: Keep Activity Monitor open
3. **Close Applications**: Free up memory before training
4. **Conservative Settings**: Use default parameters
5. **Regular Backups**: Keep multiple model backups

### **For 16GB+ RAM Systems**
1. **Train More**: Can handle 3-4 technologies
2. **Aggressive Settings**: Use higher parameters
3. **Parallel Processing**: Can run multiple scrapers
4. **Larger Datasets**: Can handle more training examples

### **General Best Practices**
1. **Test Incrementally**: Start with sample data
2. **Monitor Logs**: Check training.log regularly
3. **Keep Backups**: Never delete original model
4. **Validate Results**: Test new model before using
5. **Document Changes**: Keep track of what was trained

## 📈 Performance Optimization

### **Memory Optimization**
```bash
# Reduce memory usage during training
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_ORIGINS=*
export OLLAMA_MODELS=/tmp/ollama_models  # Use temp directory
```

### **Storage Optimization**
```bash
# Clean up old backups (keep last 3)
ls -t model_backups/ | tail -n +4 | xargs rm -rf

# Compress training data
gzip training_data/training_dataset.jsonl
```

### **Network Optimization**
```bash
# Use local caching for documentation
# - Scrape once, reuse data
# - Use offline documentation when possible
# - Cache downloaded content
```

## 🔄 Continuous Training

### **Incremental Training**
```bash
# Add new technologies to existing model
python xprr_agent.py scrape-docs --technology terraform
python xprr_agent.py create-dataset
# Fine-tune existing model with new data
```

### **Scheduled Training**
```bash
# Weekly documentation updates
0 2 * * 0 /path/to/x-pull-request-reviewer/scripts/safe_training.py
```

### **Automated Validation**
```bash
# Test model performance after training
python xprr_agent.py review --repo ./test-project --branch feature --no-interactive
```

## 📋 Training Checklist

### **Before Training**
- [ ] System has 8GB+ RAM available
- [ ] 5GB+ disk space available
- [ ] Ollama is running (`ollama serve`)
- [ ] Original model is working (`ollama list`)
- [ ] Unnecessary applications are closed

### **During Training**
- [ ] Monitor `training.log` for progress
- [ ] Check system resources in Activity Monitor
- [ ] Don't run other memory-intensive applications
- [ ] Keep system plugged in (if laptop)

### **After Training**
- [ ] Verify new model exists (`ollama list`)
- [ ] Test new model with sample code
- [ ] Update configuration to use new model
- [ ] Keep backup of original model
- [ ] Generate training report

## 🎉 Success Indicators

### **Training Success**
- ✅ New model appears in `ollama list`
- ✅ Model responds to code review prompts
- ✅ No errors in `training.log`
- ✅ System resources remain stable

### **Quality Indicators**
- ✅ Model provides technology-specific feedback
- ✅ Suggestions include file paths and line numbers
- ✅ Security and performance issues are identified
- ✅ Best practices from official docs are referenced

## 🆘 Getting Help

### **Logs and Debugging**
```bash
# Check training logs
cat training.log

# Check Ollama logs
ollama logs

# Check system resources
top -l 1
```

### **Common Commands**
```bash
# List all models
ollama list

# Remove failed model
ollama rm codellama-trained-YYYYMMDD_HHMMSS

# Restart Ollama
pkill ollama && ollama serve

# Check model info
ollama show codellama:7b-instruct
```

### **Support Resources**
- **Training Logs**: `training.log`
- **System Logs**: Console.app → System Reports
- **Ollama Documentation**: https://ollama.ai/docs
- **Project Issues**: GitHub repository

---

**Ready to train your model safely?** Start with the quick start guide and follow the safety measures to ensure a successful training process! 🚀 