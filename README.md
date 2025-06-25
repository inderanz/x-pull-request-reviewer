# x-pull-request-reviewer

**Enterprise-grade, offline, LLM-powered pull request reviewer** with interactive change management and official documentation training capabilities.

## 🚀 Features

### Core Review Capabilities
- **Multi-language Support**: Go, Java, Python, Terraform, YAML, Shell
- **Static Analysis**: Format and lint checks for each language
- **LLM-powered Reviews**: Uses Ollama (local LLM) for intelligent code review
- **Security & Compliance**: Checks for security issues, compliance problems, and best practices
- **Dependency Analysis**: Analyzes dependencies for risks and outdated packages
- **Test Coverage**: Analyzes test coverage and quality
- **Documentation**: Reviews documentation quality and completeness

### 🎯 Interactive Change Management
- **Selective Application**: Choose which suggestions to apply or ignore
- **Change Tracking**: Track all applied changes with unique IDs
- **Revert Capability**: Revert specific changes or all changes in a file
- **Batch Operations**: Apply/revert multiple changes at once
- **CI/CD Ready**: Non-interactive mode for automated environments

### 📚 Official Documentation Training
- **Documentation Scraping**: Gather official docs from technology websites
- **Training Data Generation**: Create datasets for LLM fine-tuning
- **Technology Detection**: Automatically detect technologies in code
- **Enhanced Prompts**: Use official documentation knowledge in reviews
- **Multi-technology Support**: Handle mixed technology codebases

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- Git
- Ollama (for local LLM)

### Quick Install
```bash
# Clone the repository
# (or extract the offline package)
cd x-pull-request-reviewer

# Install dependencies (all requirements are included in the offline package)
pip install -r requirements.txt

# Start Ollama (if not already running)
ollama serve
```

## 🚀 Quick Start

### Basic Code Review
```bash
# Review a local repository
python -m xprr_agent review --repo <path-to-your-repo> --branch main --no-interactive
```

> **Note:** Use `python -m xprr_agent` instead of `python xprr_agent.py` for all commands.

### Interactive Change Management
```bash
# Review with interactive change management
python xprr_agent.py review --repo ./my-project --branch feature-branch

# The system will prompt you to:
# 1. Choose which suggestions to apply
# 2. Revert changes if needed
# 3. Track all modifications
```

### Training with Official Documentation
```bash
# Create sample training data
python xprr_agent.py scrape-docs --sample-only

# Scrape Go documentation
python xprr_agent.py scrape-docs --technology go --max-pages 20

# Create training dataset
python xprr_agent.py create-dataset

# List supported technologies
python xprr_agent.py list-technologies
```

## 📖 Usage Guide

### Interactive Change Management

The system provides an interactive interface for managing code review suggestions:

```
📝 ACTIONABLE CHANGES (3):
  [1] src/main.py:15: Add input validation for user_id parameter
      Reason: Security vulnerability - missing input validation
      Current: user_id = request.args.get('user_id')

  [2] src/utils.py:23: Consider using a more descriptive variable name
      Reason: Code readability - variable name is too generic
      Current: data = process_data(input_data)

  [3] src/database.py:45: Add error handling for database connection
      Reason: Robustness - missing exception handling
      Current: connection = db.connect()

CHANGE APPLICATION OPTIONS
--------------------------------------------------------------------------------
You can apply specific changes using the following options:
• Enter suggestion ID (e.g., '1') to apply a specific change
• Enter 'all' to apply all suggested changes
• Enter 'none' to skip all changes
• Enter multiple IDs separated by commas (e.g., '1,3,5')

Enter your choice: 1,3
```

### Training System

#### Phase 1: Documentation Scraping
```bash
# Scrape specific technology
python xprr_agent.py scrape-docs --technology go --max-pages 30

# Scrape all technologies (takes longer)
python xprr_agent.py scrape-docs --max-pages 25 --delay 3.0
```

#### Phase 2: Training Dataset Creation
```bash
# Create dataset from scraped data
python xprr_agent.py create-dataset

# Create dataset for specific technology
python xprr_agent.py create-dataset --technology go
```

#### Phase 3: Enhanced Reviews
The enhanced prompts automatically use the trained knowledge:
```bash
# Review with enhanced prompts
python xprr_agent.py review --repo ./my-project --branch feature-branch
```

## 🔧 Configuration

### Environment Variables
```bash
# LLM Configuration
export LLM_HOST=http://localhost
export LLM_PORT=11434
export LLM_MODEL=codellama

# GitHub Integration
export GITHUB_TOKEN=your_github_token_here
```

### Configuration File
Edit `config/default.yaml`:
```yaml
llm:
  provider: ollama
  model: codellama
  port: 11434
github:
  token: your_github_token_here
  api_url: https://api.github.com
agent:
  mode: background
  log_level: INFO
```

## 🏗️ Architecture

### Core Components
- **Agent**: Main orchestration and review logic
- **LLM**: Ollama integration and prompt management
- **Adapters**: Language-specific static analysis
- **Review Engines**: Security, compliance, best practices
- **Change Manager**: Interactive change tracking and reversion
- **Training System**: Documentation scraping and dataset generation

### Technology Detection
The system automatically detects technologies in your code:
- **Go**: `package main`, `import`, `func`, `goroutine`
- **Java**: `public class`, `import java`, `extends`
- **Python**: `import`, `def`, `class`, `if __name__`
- **Terraform**: `terraform`, `resource`, `data`, `variable`
- **Kubernetes**: `apiVersion:`, `kind:`, `metadata:`, `spec:`
- **Helm**: `apiVersion:`, `kind: Chart`, `values:`, `{{`
- **FluxCD**: `apiVersion: source.toolkit.fluxcd.io`
- **ArgoCD**: `apiVersion: argoproj.io/v1alpha1`

## 📚 Supported Technologies

| Technology | Documentation | Focus Areas |
|------------|---------------|-------------|
| **Go** | https://golang.org/doc/ | Concurrency, performance, idioms |
| **Java** | https://docs.oracle.com/en/java/javase/ | OOP design, patterns, security |
| **Python** | https://docs.python.org/3/ | Pythonic code, performance, readability |
| **Terraform** | https://registry.terraform.io/ | Syntax, modules, state management |
| **Kubernetes** | https://kubernetes.io/docs/ | Manifests, resource management, security |
| **Helm** | https://helm.sh/docs/ | Templates, values, best practices |
| **FluxCD** | https://fluxcd.io/docs/ | GitOps, deployment patterns |
| **ArgoCD** | https://argo-cd.readthedocs.io/ | Deployment flows, sync strategies |

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_change_manager.py -v

# Run with coverage
python -m pytest --cov=agent --cov=llm --cov=review
```

## 🔄 CI/CD Integration

### Non-Interactive Mode
```bash
# Use in CI/CD pipelines
python xprr_agent.py review --repo ./project --branch feature --no-interactive
```

### Automated Training
```bash
# Weekly documentation updates
python xprr_agent.py scrape-docs --technology go --max-pages 10
python xprr_agent.py create-dataset
# Trigger model retraining
```

## 📖 Documentation

- [Training Guide](docs/training_guide.md) - Complete guide to training with official documentation
- [Interactive Review Example](examples/interactive_review_example.md) - Real-world usage examples
- [API Documentation](docs/api.md) - Developer API reference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Code Llama](https://github.com/facebookresearch/codellama) for code understanding
- Official documentation sites for training data
- Open source community for inspiration and feedback

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the [docs](docs/) directory
- **Examples**: See [examples](examples/) for usage patterns
- **Training**: Follow the [training guide](docs/training_guide.md)

---

**Ready to revolutionize your code review process?** Start with the quick start guide and explore the interactive change management and training capabilities! 🚀 