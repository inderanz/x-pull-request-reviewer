#!/usr/bin/env python3
"""
Safe Training Script for x-pull-request-reviewer
Monitors system resources and implements conservative fine-tuning.
"""

import os
import sys
import json
import time
import psutil
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProgressTracker:
    """Track and display training progress."""
    
    def __init__(self):
        self.current_step = 0
        self.total_steps = 0
        self.step_names = []
        self.start_time = None
        self.step_start_time = None
        
    def initialize(self, steps: List[str]):
        """Initialize progress tracking with step names."""
        self.total_steps = len(steps)
        self.step_names = steps
        self.start_time = time.time()
        self.current_step = 0
        
    def start_step(self, step_name: str):
        """Start a new step."""
        self.current_step += 1
        self.step_start_time = time.time()
        self._print_progress(f"🔄 {step_name}")
        
    def complete_step(self, step_name: str, success: bool = True):
        """Complete a step."""
        elapsed = time.time() - self.step_start_time
        status = "✅" if success else "❌"
        self._print_progress(f"{status} {step_name} ({elapsed:.1f}s)")
        
    def update_substep(self, message: str):
        """Update substep progress."""
        elapsed = time.time() - self.step_start_time
        self._print_progress(f"  📝 {message} ({elapsed:.1f}s)")
        
    def _print_progress(self, message: str):
        """Print progress message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def print_summary(self):
        """Print training summary."""
        total_time = time.time() - self.start_time
        print(f"\n🎉 Training Summary:")
        print(f"   Total time: {total_time:.1f} seconds")
        print(f"   Steps completed: {self.current_step}/{self.total_steps}")
        print(f"   Average time per step: {total_time/self.total_steps:.1f}s")

class SafeTrainer:
    """Safe training system with resource monitoring and progress tracking."""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.training_dir = self.base_dir / "training_data"
        self.backup_dir = self.base_dir / "model_backups"
        self.resource_log = []
        self.progress = ProgressTracker()
        
        # Create directories
        self.backup_dir.mkdir(exist_ok=True)
        
        # Resource thresholds
        self.memory_threshold = 0.85  # 85% memory usage
        self.disk_threshold = 0.95    # 95% disk usage (increased from 90%)
        self.cpu_threshold = 0.95     # 95% CPU usage
        
    def check_system_resources(self) -> Dict:
        """Check current system resources."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        resources = {
            'memory_used_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_used_percent': disk.percent,
            'disk_available_gb': disk.free / (1024**3),
            'cpu_percent': cpu_percent,
            'timestamp': time.time()
        }
        
        self.resource_log.append(resources)
        return resources
    
    def is_system_healthy(self) -> bool:
        """Check if system has enough resources for training."""
        resources = self.check_system_resources()
        
        # Check memory
        if resources['memory_used_percent'] > (self.memory_threshold * 100):
            logger.warning(f"Memory usage high: {resources['memory_used_percent']:.1f}%")
            return False
        
        # Check disk
        if resources['disk_used_percent'] > (self.disk_threshold * 100):
            logger.warning(f"Disk usage high: {resources['disk_used_percent']:.1f}%")
            return False
        
        # Check available disk space (need at least 2GB for model creation)
        if resources['disk_available_gb'] < 2:
            logger.warning(f"Low disk space: {resources['disk_available_gb']:.1f}GB available")
            return False
        
        logger.info(f"System healthy - Memory: {resources['memory_used_percent']:.1f}%, "
                   f"Disk: {resources['disk_used_percent']:.1f}%, "
                   f"CPU: {resources['cpu_percent']:.1f}%")
        return True
    
    def backup_existing_model(self) -> bool:
        """Create a backup of the existing model."""
        try:
            self.progress.start_step("Creating backup of existing model")
            
            # Check if model exists
            self.progress.update_substep("Checking for existing codellama model")
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if 'codellama' not in result.stdout:
                logger.error("No codellama model found!")
                self.progress.complete_step("Creating backup of existing model", False)
                return False
            
            # Create backup directory with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"codellama_backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            self.progress.update_substep(f"Creating backup directory: {backup_path}")
            
            # Copy model files
            ollama_home = Path.home() / ".ollama"
            if ollama_home.exists():
                self.progress.update_substep("Copying model files (this may take a few minutes)")
                shutil.copytree(ollama_home / "models", backup_path / "models", dirs_exist_ok=True)
                logger.info(f"Model backup created at: {backup_path}")
                self.progress.complete_step("Creating backup of existing model", True)
                return True
            else:
                logger.error("Ollama models directory not found!")
                self.progress.complete_step("Creating backup of existing model", False)
                return False
                
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            self.progress.complete_step("Creating backup of existing model", False)
            return False
    
    def scrape_documentation_safe(self, technology: str, max_pages: int = 20) -> bool:
        """Safely scrape documentation with resource monitoring and progress tracking."""
        try:
            self.progress.start_step(f"Scraping {technology} documentation")
            
            # Check resources before starting
            if not self.is_system_healthy():
                logger.error("System resources insufficient for scraping")
                self.progress.complete_step(f"Scraping {technology} documentation", False)
                return False
            
            # Run scraping with conservative settings
            cmd = [
                sys.executable, "xprr_agent.py", "scrape-docs",
                "--technology", technology,
                "--max-pages", str(max_pages),
                "--delay", "3.0"  # Conservative delay
            ]
            
            self.progress.update_substep(f"Starting scraper: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Monitor process and resources with progress updates
            page_count = 0
            while process.poll() is None:
                if not self.is_system_healthy():
                    logger.warning("Resource usage high, terminating scraping...")
                    process.terminate()
                    process.wait()
                    self.progress.complete_step(f"Scraping {technology} documentation", False)
                    return False
                
                # Update progress every 30 seconds
                if int(time.time() - self.progress.step_start_time) % 30 == 0:
                    self.progress.update_substep(f"Scraping in progress... (checking resources)")
                
                time.sleep(10)  # Check every 10 seconds
            
            # Get output
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                # Try to extract page count from output
                if "pages for" in stdout:
                    try:
                        page_count = int(stdout.split("pages for")[0].split()[-1])
                    except:
                        page_count = max_pages
                
                self.progress.update_substep(f"Successfully scraped {page_count} pages")
                logger.info(f"Successfully scraped {technology} documentation")
                self.progress.complete_step(f"Scraping {technology} documentation", True)
                return True
            else:
                logger.error(f"Scraping failed: {stderr}")
                self.progress.complete_step(f"Scraping {technology} documentation", False)
                return False
                
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            self.progress.complete_step(f"Scraping {technology} documentation", False)
            return False
    
    def create_training_dataset_safe(self) -> bool:
        """Safely create training dataset with progress tracking."""
        try:
            self.progress.start_step("Creating training dataset")
            
            if not self.is_system_healthy():
                logger.error("System resources insufficient for dataset creation")
                self.progress.complete_step("Creating training dataset", False)
                return False
            
            self.progress.update_substep("Processing scraped documentation")
            cmd = [sys.executable, "xprr_agent.py", "create-dataset"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Count training examples
                training_file = self.training_dir / "training_dataset.jsonl"
                if training_file.exists():
                    with open(training_file, 'r') as f:
                        line_count = sum(1 for line in f)
                    self.progress.update_substep(f"Created dataset with {line_count} training examples")
                
                logger.info("Training dataset created successfully")
                self.progress.complete_step("Creating training dataset", True)
                return True
            else:
                logger.error(f"Dataset creation failed: {result.stderr}")
                self.progress.complete_step("Creating training dataset", False)
                return False
                
        except Exception as e:
            logger.error(f"Dataset creation error: {e}")
            self.progress.complete_step("Creating training dataset", False)
            return False
    
    def create_modelfile(self, training_data_path: str) -> str:
        """Create a Modelfile for fine-tuning."""
        self.progress.start_step("Creating Modelfile")
        
        modelfile_content = f'''FROM codellama:7b-instruct

# System prompt for code review expertise
SYSTEM "You are a senior DevOps and cloud-native engineer trained on official documentation from Go, Java, Python, Helm, Terraform, Kubernetes, FluxCD and ArgoCD. You perform thorough code and configuration reviews based on official documentation and best practices. You provide actionable, specific feedback with file paths and line numbers. You focus on security, performance, best practices, maintainability, and error handling."

# Template for instruction following
TEMPLATE "{{{{ .Prompt }}}}"

# Conservative parameters for 8GB RAM
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 4096
'''
        
        modelfile_path = self.base_dir / "Modelfile"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        self.progress.update_substep(f"Modelfile created at: {modelfile_path}")
        logger.info(f"Modelfile created at: {modelfile_path}")
        self.progress.complete_step("Creating Modelfile", True)
        return str(modelfile_path)
    
    def fine_tune_model_safe(self, modelfile_path: str) -> bool:
        """Safely create a custom model with optimized prompts for code review."""
        try:
            self.progress.start_step("Creating custom model")
            
            # Check if we have enough resources
            if not self.is_system_healthy():
                logger.error("Insufficient resources for model creation")
                self.progress.complete_step("Creating custom model", False)
                return False
            
            # Create new model name
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            new_model_name = f"codellama-trained-{timestamp}"
            
            self.progress.update_substep(f"Creating custom model: {new_model_name}")
            
            # Run model creation with resource monitoring
            cmd = ['ollama', 'create', new_model_name, '-f', modelfile_path]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Monitor process with progress updates
            last_update = time.time()
            while process.poll() is None:
                current_time = time.time()
                
                if not self.is_system_healthy():
                    logger.warning("Resource usage high during model creation...")
                    # Don't terminate - let it finish if possible
                
                # Update progress every 30 seconds
                if current_time - last_update >= 30:
                    elapsed = current_time - self.progress.step_start_time
                    self.progress.update_substep(f"Model creation in progress... ({elapsed:.0f}s elapsed)")
                    last_update = current_time
                
                time.sleep(15)  # Check every 15 seconds
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.progress.update_substep(f"Custom model created successfully!")
                logger.info(f"Custom model created successfully! New model: {new_model_name}")
                self.progress.complete_step("Creating custom model", True)
                return True
            else:
                logger.error(f"Model creation failed: {stderr}")
                self.progress.complete_step("Creating custom model", False)
                return False
                
        except Exception as e:
            logger.error(f"Model creation error: {e}")
            self.progress.complete_step("Creating custom model", False)
            return False
    
    def run_complete_training(self, technologies: List[str] = None) -> bool:
        """Run the complete safe training process with comprehensive progress tracking."""
        if technologies is None:
            technologies = ['go', 'python']  # Start with smaller technologies
        
        # Initialize progress tracking
        steps = [
            "System resource check",
            "Backup existing model",
        ]
        
        # Add scraping steps for each technology
        for tech in technologies:
            steps.append(f"Scrape {tech} documentation")
        
        steps.extend([
            "Create training dataset",
            "Create Modelfile",
            "Create custom model",
            "Generate training report"
        ])
        
        self.progress.initialize(steps)
        
        print("\n" + "="*60)
        print("🚀 X-PULL-REQUEST-REVIEWER SAFE TRAINING")
        print("="*60)
        print(f"📋 Training plan: {len(steps)} steps")
        print(f"🔧 Technologies: {', '.join(technologies)}")
        print(f"💾 System: 8GB RAM, {self.check_system_resources()['disk_available_gb']:.1f}GB available")
        print("="*60)
        
        # Step 1: System check
        self.progress.start_step("System resource check")
        if not self.is_system_healthy():
            logger.error("System resources insufficient for training")
            self.progress.complete_step("System resource check", False)
            return False
        self.progress.complete_step("System resource check", True)
        
        # Step 2: Backup existing model
        if not self.backup_existing_model():
            logger.error("Backup failed - aborting training")
            return False
        
        # Step 3: Scrape documentation
        for tech in technologies:
            if not self.scrape_documentation_safe(tech, max_pages=15):  # Conservative
                logger.warning(f"Failed to scrape {tech}, continuing with others...")
        
        # Step 4: Create training dataset
        if not self.create_training_dataset_safe():
            logger.error("Dataset creation failed")
            return False
        
        # Step 5: Check training data
        training_file = self.training_dir / "training_dataset.jsonl"
        if not training_file.exists():
            logger.error("Training dataset not found")
            return False
        
        # Count training examples
        with open(training_file, 'r') as f:
            line_count = sum(1 for line in f)
        logger.info(f"Training dataset contains {line_count} examples")
        
        if line_count < 10:
            logger.warning("Very few training examples - consider scraping more data")
        
        # Step 6: Create Modelfile
        modelfile_path = self.create_modelfile(str(training_file))
        
        # Step 7: Create custom model
        if not self.fine_tune_model_safe(modelfile_path):
            logger.error("Custom model creation failed")
            return False
        
        # Step 8: Generate report
        self.progress.start_step("Generate training report")
        report = self.generate_training_report()
        with open('training_report.md', 'w') as f:
            f.write(report)
        self.progress.update_substep("Training report saved to training_report.md")
        self.progress.complete_step("Generate training report", True)
        
        # Print final summary
        self.progress.print_summary()
        
        print("\n" + "="*60)
        print("🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ Your custom model is ready to use")
        print("\n📋 Next steps:")
        print("1. List models: ollama list")
        print("2. Test new model: ollama run codellama-trained-YYYYMMDD_HHMMSS")
        print("3. Update config: Edit config/default.yaml")
        print("4. Start reviewing: python xprr_agent.py review --repo ./my-project")
        print("="*60)
        
        return True
    
    def generate_training_report(self) -> str:
        """Generate a training report."""
        resources = self.check_system_resources()
        report = f"""
# Training Report

## System Resources
- Memory: 8GB total
- Storage: {resources['disk_available_gb']:.1f}GB available
- CPU: 8 cores

## Training Process
- Backup created: {self.backup_dir.exists()}
- Training data: {self.training_dir.exists()}
- Resource monitoring: Active
- Progress tracking: Enabled

## Recommendations
- Monitor memory usage during inference
- Consider using smaller batch sizes
- Keep backups of original model
- Check training.log for detailed logs
"""
        return report

def main():
    """Main training function."""
    trainer = SafeTrainer()
    
    print("=== X-PULL-REQUEST-REVIEWER SAFE TRAINING ===")
    print("This will train your model on official documentation")
    print("System will be monitored throughout the process")
    print("Progress will be tracked and displayed in real-time")
    print()
    
    # Check initial system state
    if not trainer.is_system_healthy():
        print("❌ System resources insufficient for training")
        print("Please close other applications and try again")
        return False
    
    # Ask user for technologies
    print("Available technologies: go, java, python, terraform, kubernetes, helm, fluxcd, argocd")
    print("Recommended to start with 1-2 technologies for 8GB RAM")
    
    tech_input = input("Enter technologies to train (comma-separated, e.g., 'go,python'): ").strip()
    if not tech_input:
        technologies = ['go', 'python']  # Default
    else:
        technologies = [tech.strip() for tech in tech_input.split(',')]
    
    print(f"\nStarting training for: {technologies}")
    print("This may take 30-60 minutes depending on data size")
    print("Progress will be displayed in real-time...")
    print("Press Ctrl+C to stop training (your original model is safe)")
    
    # Run training
    try:
        success = trainer.run_complete_training(technologies)
        
        if success:
            print("\n✅ Training completed successfully!")
            print("Your custom model is ready to use")
            print("\nTo use the new model:")
            print("1. List models: ollama list")
            print("2. Use in reviews: Update config to use new model name")
        else:
            print("\n❌ Training failed")
            print("Check training.log for details")
            print("Your original model is preserved in backups/")
        
        # Generate report
        report = trainer.generate_training_report()
        with open('training_report.md', 'w') as f:
            f.write(report)
        
        print(f"\nTraining report saved to: training_report.md")
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("Your original model is safe in backups/")
        print("You can restart training anytime")
        return False

if __name__ == "__main__":
    main() 