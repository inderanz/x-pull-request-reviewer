# 🚀 X-Pull-Request-Reviewer (Enterprise Edition)

**Enterprise-Grade, Offline, LLM-Powered Code Review Agent**

Secure | Air-Gapped | Multi-Language | Plug-and-Play

---

## ✨ Overview

X-Pull-Request-Reviewer (XPRR) is a production-ready, enterprise-grade code review agent that automatically analyzes pull requests and provides actionable feedback. It supports multiple LLM providers including Ollama (offline), Gemini CLI, and Google Code Assist.

## 🎯 Features

- **🔒 Offline Capable**: Works with local Ollama models for air-gapped environments
- **🤖 Multi-LLM Support**: Ollama, Gemini CLI, Google Code Assist
- **🌍 Multi-Language**: Python, Java, Go, Terraform, YAML, Shell, and more
- **🔍 Comprehensive Analysis**: Security, compliance, best practices, dependencies
- **📝 Line-by-Line Comments**: Detailed feedback on specific code lines
- **⚡ Fast & Efficient**: Optimized for production workloads
- **🔧 Easy Setup**: One-command installation and configuration

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **Node.js & npm** (for Gemini CLI)
- **Git** (recommended)

### 2. Installation

```bash
# Clone or download the xprr-production directory
cd xprr-production

# Run the setup script
./setup.sh
```

The setup script will:
- ✅ Install Python dependencies
- ✅ Install Gemini CLI (if Node.js is available)
- ✅ Create necessary directories
- ✅ Set up configuration files
- ✅ Prompt for API keys

### 3. First Run

```bash
# Check if everything is working
./xprr status

# Review your first PR
./xprr review https://github.com/org/repo/pull/123
```

## 🔧 Configuration

### LLM Providers

XPRR supports three LLM providers:

#### 1. **Ollama (Offline)** - Default
```bash
# Uses local Ollama models - no internet required
./xprr review https://github.com/org/repo/pull/123
```

#### 2. **Gemini CLI** - Recommended for online use
```bash
# Uses Google's Gemini model via CLI
./xprr review https://github.com/org/repo/pull/123 --provider gemini_cli
```

#### 3. **Google Code Assist**
```bash
# Uses Google Code Assist API
./xprr review https://github.com/org/repo/pull/123 --provider google_code_assist
```

### API Key Setup

#### Gemini CLI
```bash
# The setup script will prompt for your API key
# Or set it manually:
export GEMINI_API_KEY="your-api-key-here"

# Get your API key from: https://makersuite.google.com/app/apikey
```

#### Google Code Assist
```bash
# Set your Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

## 📋 Usage

### Basic Commands

```bash
# Setup dependencies and credentials
./xprr setup

# Check agent status
./xprr status

# Review a pull request
./xprr review <PR_URL>

# Review with specific provider
./xprr review <PR_URL> --provider gemini_cli

# Non-interactive mode (for CI/CD)
./xprr review <PR_URL> --no-interactive

# Stop the agent
./xprr stop

# Check air-gap readiness
./xprr check-airgap
```

### Advanced Usage

```bash
# Review by PR number and repo slug
./xprr review --pr-number 123 --repo-slug org/repo

# Review with specific provider and non-interactive
./xprr review --pr-number 123 --repo-slug org/repo --provider gemini_cli --no-interactive
```

## 🔍 What XPRR Analyzes

### Security Analysis
- 🔐 Hardcoded credentials
- 🚨 SQL injection vulnerabilities
- ⚠️ XSS vulnerabilities
- 🔑 Secret scanning
- 🛡️ Input validation issues

### Compliance Checks
- 📄 License compliance
- ©️ Copyright issues
- 🌍 Export control compliance
- 📋 Regulatory requirements

### Best Practices
- 📝 Documentation quality
- 🧪 Test coverage
- 🔧 Code formatting
- 📚 Dependency management
- 🏗️ Architecture patterns

### Language-Specific Analysis
- **Python**: Black formatting, flake8 linting, docstrings
- **Java**: Google Java Format, Checkstyle
- **Go**: gofmt, golint
- **Terraform**: terraform fmt, tflint
- **YAML**: yamllint, prettier
- **Shell**: shfmt, shellcheck

## 🏗️ Architecture

```
xprr-production/
├── src/                    # Source code
│   ├── agent/             # Core agent logic
│   ├── adapters/          # Language-specific adapters
│   ├── llm/               # LLM provider integrations
│   ├── review/            # Review engines
│   └── github/            # GitHub API client
├── tests/                 # Test suite
├── config/                # Configuration files
├── bin/                   # Binary dependencies
├── packages/              # Python wheel packages
├── ollama_models/         # Ollama model files
├── logs/                  # Log files
├── xprr                   # Main CLI script
├── setup.sh               # Setup script
└── README.md              # This file
```

## 🔧 Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_adapters.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Adding New Language Support
1. Create adapter in `src/adapters/`
2. Add language detection in `src/agent/static_analysis.py`
3. Add test cases in `tests/`
4. Update documentation

### Adding New LLM Provider
1. Create client in `src/llm/`
2. Add to unified client in `src/llm/unified_client.py`
3. Add credential management in `src/llm/credential_manager.py`
4. Update CLI options in `xprr`

## 🚀 Deployment

### Docker Deployment
```bash
# Build the image
docker build -t xprr .

# Run the container
docker run -it --rm xprr review <PR_URL>
```

### CI/CD Integration
```bash
# Non-interactive mode for automation
./xprr review <PR_URL> --no-interactive --provider gemini_cli
```

### Air-Gapped Deployment
1. Download all wheel packages to `packages/`
2. Download Ollama models to `ollama_models/`
3. Run `./xprr check-airgap` to verify readiness
4. Use `--provider ollama` for offline operation

## 📊 Performance

- **Review Speed**: 30-60 seconds per PR (depending on size and provider)
- **Memory Usage**: 100-500MB (depending on model size)
- **CPU Usage**: Moderate during analysis
- **Network**: Minimal (except for API calls)

## 🔒 Security

- **No Code Execution**: XPRR only analyzes code, never executes it
- **Secure Credentials**: API keys stored in system keyring
- **Air-Gapped**: Can operate completely offline
- **Audit Trail**: All actions logged for compliance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Developer**: Inder Chauhan
- **Organization**: https://anzx.ai/
- **Team**: X-agents Team

---

## 🆘 Support

### Common Issues

**Q: Gemini CLI installation fails**
A: Ensure Node.js and npm are installed. Run `node --version` and `npm --version` to verify.

**Q: API key not working**
A: Check that your API key is correct and has the necessary permissions.

**Q: Ollama model not found**
A: Run `./xprr setup` to install the required model.

**Q: Permission denied on xprr script**
A: Run `chmod +x xprr` to make it executable.

### Getting Help

- 📖 Check the documentation in `docs/`
- 🐛 Report issues with detailed logs
- 💬 Ask questions in the community

---

**Happy reviewing! 🚀** 