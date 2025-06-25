# Training Guide for x-pull-request-reviewer

This guide explains how to train your x-pull-request-reviewer LLM with official documentation from various technologies to improve code review capabilities.

## Overview

The training system allows you to:

1. **Scrape official documentation** from technology websites
2. **Create training datasets** from the scraped content
3. **Enhance LLM prompts** with technology-specific knowledge
4. **Improve code review quality** with official best practices

## Supported Technologies

The system supports training on official documentation from:

| Technology | Documentation URL | Focus Areas |
|------------|------------------|-------------|
| **Go** | https://golang.org/doc/ | Concurrency, performance, idioms, best practices |
| **Java** | https://docs.oracle.com/en/java/javase/ | OOP design, patterns, performance, security |
| **Python** | https://docs.python.org/3/ | Pythonic code, performance, readability, best practices |
| **Terraform** | https://registry.terraform.io/ | Syntax, modules, variables, state management |
| **Kubernetes** | https://kubernetes.io/docs/ | Manifests, resource management, anti-patterns, security |
| **Helm** | https://helm.sh/docs/ | Templates, values, YAML logic, best practices |
| **FluxCD** | https://fluxcd.io/docs/ | GitOps, deployment patterns, YAML configs |
| **ArgoCD** | https://argo-cd.readthedocs.io/ | Deployment flows, sync strategies, YAML configs |

## Quick Start

### 1. Create Sample Training Data

Start by creating sample training data to understand the format:

```bash
python xprr_agent.py scrape-docs --sample-only
```

This creates a sample training file at `training_data/sample_training.jsonl`.

### 2. Scrape Official Documentation

Scrape documentation for a specific technology:

```bash
# Scrape Go documentation
python xprr_agent.py scrape-docs --technology go --max-pages 20

# Scrape Python documentation
python xprr_agent.py scrape-docs --technology python --max-pages 30

# Scrape all technologies (takes longer)
python xprr_agent.py scrape-docs --max-pages 25 --delay 3.0
```

### 3. Create Training Dataset

Process the scraped documentation into a training dataset:

```bash
# Create dataset from all scraped data
python xprr_agent.py create-dataset

# Create dataset for specific technology
python xprr_agent.py create-dataset --technology go

# Specify custom output file
python xprr_agent.py create-dataset --output-file my_training_data.jsonl
```

## Detailed Usage

### Scraping Documentation

The `scrape-docs` command has several options:

```bash
python xprr_agent.py scrape-docs [OPTIONS]

Options:
  --technology TEXT    Specific technology to scrape
  --output-dir TEXT    Output directory for scraped data (default: training_data)
  --max-pages INTEGER  Maximum pages to scrape per technology (default: 30)
  --delay FLOAT        Delay between requests in seconds (default: 2.0)
  --sample-only        Only create sample training data (no web scraping)
```

**Important Notes:**
- Be respectful of rate limits (use `--delay` to control request frequency)
- Start with small `--max-pages` values to test
- The scraper respects robots.txt and uses appropriate user agents
- Some sites may block automated requests

### Creating Training Datasets

The `create-dataset` command processes scraped documentation:

```bash
python xprr_agent.py create-dataset [OPTIONS]

Options:
  --input-dir TEXT     Directory containing scraped documentation
  --output-file TEXT   Output file for training dataset
  --technology TEXT    Filter by specific technology
```

### Listing Supported Technologies

View information about supported technologies:

```bash
# List all supported technologies
python xprr_agent.py list-technologies

# Get details for specific technology
python xprr_agent.py list-technologies --technology go
```

## Training Data Format

The system creates training data in JSONL format suitable for fine-tuning:

```json
{
  "prompt": "You are learning from the official documentation of GO...",
  "response": "Based on the GO official documentation:\n\n## Key Points Summary...",
  "technology": "go",
  "type": "documentation_ingestion"
}
```

### Training Data Types

1. **Documentation Ingestion**: Learning from official documentation
2. **Code Review**: Reviewing code examples from documentation
3. **Best Practices**: Understanding recommended patterns
4. **Security Guidelines**: Learning security considerations
5. **Performance Tips**: Understanding optimization strategies

## Using Enhanced Prompts

The enhanced review system automatically:

1. **Detects technologies** in your code
2. **Applies technology-specific** review strategies
3. **Uses official documentation** knowledge
4. **Provides structured feedback** with priorities

### Technology Detection

The system automatically detects technologies in your code:

```python
# Go code
package main
import "fmt"
func main() { ... }

# Python code
import os
def main(): ...

# Terraform code
resource "aws_instance" "example" { ... }

# Kubernetes manifests
apiVersion: v1
kind: Pod
metadata: ...
```

### Enhanced Review Prompts

The system uses different prompts based on detected technologies:

- **Single Technology**: Focused review with technology-specific knowledge
- **Multi-Technology**: Cross-technology integration review
- **Infrastructure**: IaC and configuration review
- **General**: Fallback for unknown technologies

## Training Workflow

### Phase 1: Documentation Ingestion

```bash
# Scrape documentation
python xprr_agent.py scrape-docs --technology go

# Create training data
python xprr_agent.py create-dataset --technology go
```

### Phase 2: Model Training

Use the generated training data to fine-tune your LLM:

```bash
# Example with Ollama (if supported)
ollama create my-trained-model -f Modelfile

# Example with other training frameworks
# (depends on your specific LLM training setup)
```

### Phase 3: Enhanced Reviews

The enhanced prompts automatically use the trained knowledge:

```bash
# Review with enhanced prompts
python xprr_agent.py review --repo ./my-project --branch feature-branch
```

## Best Practices

### Scraping Best Practices

1. **Start Small**: Begin with `--max-pages 10` to test
2. **Respect Rate Limits**: Use `--delay 3.0` or higher
3. **Monitor Output**: Check for errors in scraped data
4. **Be Selective**: Focus on most relevant documentation sections

### Training Best Practices

1. **Quality Over Quantity**: Focus on high-quality documentation
2. **Diverse Sources**: Include multiple documentation sections
3. **Regular Updates**: Re-scrape documentation periodically
4. **Validate Data**: Review generated training data for quality

### Review Best Practices

1. **Technology-Specific**: Use appropriate review strategies
2. **Official Standards**: Reference official documentation
3. **Structured Feedback**: Provide actionable recommendations
4. **Priority Levels**: Categorize issues by severity

## Troubleshooting

### Common Issues

1. **Scraping Errors**
   - Check internet connection
   - Verify URLs are accessible
   - Increase delay between requests
   - Check for rate limiting

2. **Training Data Quality**
   - Review scraped content manually
   - Filter out low-quality pages
   - Focus on official documentation
   - Validate JSONL format

3. **Model Performance**
   - Ensure sufficient training data
   - Use appropriate model size
   - Validate training results
   - Test with sample code

### Getting Help

1. **Check Logs**: Review error messages in output
2. **Sample Data**: Start with `--sample-only` to understand format
3. **Small Scale**: Test with single technology first
4. **Documentation**: Review this guide and code comments

## Advanced Usage

### Custom Training Prompts

You can extend the training system with custom prompts:

```python
from llm.training_prompts import create_training_dataset_entry

# Create custom training entry
entry = create_training_dataset_entry(
    technology="my-tech",
    doc_content="Custom documentation content",
    code_example="Example code"
)
```

### Multi-Technology Reviews

The system automatically handles multi-technology codebases:

```bash
# Review mixed technology project
python xprr_agent.py review --repo ./mixed-project
```

### Custom Technology Support

Add support for new technologies by extending the configuration:

```python
# Add to OFFICIAL_DOCS in training_prompts.py
"my_tech": {
    "url": "https://my-tech.org/docs/",
    "source": "https://github.com/my-tech/repo",
    "focus": ["feature1", "feature2", "best_practices"]
}
```

## Integration with CI/CD

### Non-Interactive Mode

Use the enhanced reviews in automated environments:

```bash
# CI/CD pipeline usage
python xprr_agent.py review --repo ./project --branch feature --no-interactive
```

### Training in CI/CD

Automate documentation updates:

```bash
# Weekly documentation updates
python xprr_agent.py scrape-docs --technology go --max-pages 10
python xprr_agent.py create-dataset
# Trigger model retraining
```

## Conclusion

The training system significantly enhances the x-pull-request-reviewer's capabilities by incorporating official documentation knowledge. This leads to:

- **More accurate reviews** based on official standards
- **Technology-specific insights** and best practices
- **Better security and performance** recommendations
- **Comprehensive coverage** of modern development tools

Start with the sample data, then gradually build your training dataset to create a powerful, knowledge-enhanced code review system. 