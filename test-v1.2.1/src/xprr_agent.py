BANNER = r"""
============================================================
   🚀 X-PULL-REQUEST-REVIEWER (Enterprise Edition)
============================================================
  Enterprise-Grade, Offline, LLM-Powered Code Review Agent
  Secure | Air-Gapped | Multi-Language | Plug-and-Play
============================================================
✨ Offered by https://anzx.ai/ — Personal project of Inder Chauhan
🤖 Part of the X-agents Team — Always learning, always evolving!
🙏 Thanks to its Developer Inder Chauhan for this amazing tool!
"""

# Always print banner on any CLI invocation
print(BANNER)

import click
from .agent.main import review_pr_or_branch, extract_repo_url_from_pr_url
from .llm.doc_scraper import DocumentationScraper, create_sample_training_data
import json
import os
import importlib.util
import glob
import logging

# Setup audit logger
AUDIT_LOG = os.path.join(os.getcwd(), 'logs', 'audit.log')
os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
logging.basicConfig(filename=AUDIT_LOG, level=logging.INFO, format='[%(asctime)s] %(message)s')

def log_audit(message):
    print(message)
    logging.info(message)

# Plugin loader
PLUGINS_DIR = os.path.join(os.path.dirname(__file__), 'plugins')
def load_plugins():
    plugins = []
    if os.path.isdir(PLUGINS_DIR):
        for plugin_file in glob.glob(os.path.join(PLUGINS_DIR, '*.py')):
            spec = importlib.util.spec_from_file_location("plugin", plugin_file)
            plugin = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(plugin)
                plugins.append(plugin)
                log_audit(f"Loaded plugin: {plugin_file}")
            except Exception as e:
                log_audit(f"[ERROR] Failed to load plugin {plugin_file}: {e}")
    return plugins

@click.group()
def cli():
    """x-pull-request-reviewer: Enterprise-grade, offline, LLM-powered PR reviewer."""
    pass

@cli.command()
def start():
    """Start the agent in background mode."""
    click.echo("Agent started in background mode.")

@cli.command()
@click.option('--pr', help='GitHub PR link to review')
@click.option('--repo', help='Path to local repo')
@click.option('--branch', help='Branch to review')
@click.option('--pr-number', type=int, help='Pull request number (for posting comments)')
@click.option('--repo-slug', help='GitHub repo in org/repo format (for posting comments)')
@click.option('--no-interactive', is_flag=True, help='Disable interactive change management (useful for CI/CD)')
@click.option('--provider', type=click.Choice(['ollama', 'google_code_assist', 'gemini_cli']), 
              help='LLM provider to use for the review')
def review(pr, repo, branch, pr_number, repo_slug, no_interactive, provider):
    """Review a pull request or branch. Optionally post LLM review as PR comment if --pr-number and --repo-slug are provided.
    
    The review now includes interactive change management where you can:
    - Apply specific suggested changes
    - Revert applied changes if needed
    - Selectively ignore certain recommendations

    Required GitHub token scopes: repo (for private repos), public_repo (for public repos), and write:discussion for comments.
    """
    interactive = not no_interactive
    plugins = load_plugins()
    
    # Set up provider if specified
    if provider:
        from .llm.unified_client import get_llm_client
        client = get_llm_client(provider=provider)
        if not client.switch_provider(provider):
            log_audit(f"[ERROR] Failed to switch to provider: {provider}")
            print(f"[ERROR] Failed to switch to provider: {provider}")
            return
    
    try:
        log_audit(f"[REVIEW] Starting review: pr={pr}, repo={repo}, branch={branch}, pr_number={pr_number}, repo_slug={repo_slug}, provider={provider or 'default'}")
        
        # Handle PR URL properly
        if pr and pr.startswith('http'):
            # Extract repository URL from PR URL
            repo_url = extract_repo_url_from_pr_url(pr)
            if not repo_url:
                log_audit(f"[ERROR] Could not extract repository URL from PR URL: {pr}")
                print(f"[ERROR] Could not extract repository URL from PR URL: {pr}")
                return
        else:
            repo_url = repo
        
        review_pr_or_branch(
            repo_url=repo_url, 
            repo_path=repo, 
            branch=branch, 
            base_branch=None, 
            pr_number=pr_number, 
            repo_slug=repo_slug,
            interactive=interactive,
            plugins=plugins,
            provider=provider
        )
        log_audit(f"[REVIEW] Completed review: pr={pr}, repo={repo}, branch={branch}, pr_number={pr_number}, repo_slug={repo_slug}")
    except Exception as e:
        log_audit(f"[ERROR] Review failed: {e}")
        print(f"[ERROR] Review failed: {e}")

@cli.command()
def config():
    """Show or edit agent configuration."""
    click.echo("Agent configuration management.")

@cli.command()
@click.option('--technology', help='Specific technology to scrape (go, java, python, terraform, kubernetes, helm, fluxcd, argocd, terraform-aws, terraform-kubernetes, terraform-google)')
@click.option('--output-dir', default='training_data', help='Output directory for scraped data')
@click.option('--max-pages', default=30, help='Maximum pages to scrape per technology')
@click.option('--delay', default=2.0, help='Delay between requests in seconds')
@click.option('--sample-only', is_flag=True, help='Only create sample training data (no web scraping)')
def scrape_docs(technology, output_dir, max_pages, delay, sample_only):
    """Scrape official documentation for training the LLM.
    
    This command helps gather official documentation from various technology websites
    to train the LLM for better code reviews. Supports Go, Java, Python, Terraform,
    Kubernetes, Helm, FluxCD, and ArgoCD.
    """
    if sample_only:
        click.echo("Creating sample training data...")
        sample_data = create_sample_training_data()
        
        os.makedirs(output_dir, exist_ok=True)
        sample_file = os.path.join(output_dir, "sample_training.jsonl")
        
        with open(sample_file, 'w', encoding='utf-8') as f:
            for entry in sample_data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        click.echo(f"Sample training data saved to {sample_file}")
        return
    
    scraper = DocumentationScraper(output_dir)
    
    if technology:
        # Handle Terraform provider scraping
        if technology.startswith('terraform-'):
            provider_name = technology.replace('terraform-', '')
            from .llm.training_prompts import OFFICIAL_DOCS
            if technology not in OFFICIAL_DOCS:
                click.echo(f"Error: Unsupported technology '{technology}'. Supported: {', '.join(OFFICIAL_DOCS.keys())}")
                return
            
            config = OFFICIAL_DOCS[technology]
            result = scraper.scrape_terraform_provider_docs(
                provider_name=provider_name,
                base_url=config["url"],
                max_pages=max_pages,
                delay=delay
            )
        else:
            # Scrape specific technology
            from .llm.training_prompts import OFFICIAL_DOCS
            if technology.lower() not in OFFICIAL_DOCS:
                click.echo(f"Error: Unsupported technology '{technology}'. Supported: {', '.join(OFFICIAL_DOCS.keys())}")
                return
            
            config = OFFICIAL_DOCS[technology.lower()]
            result = scraper.scrape_technology_docs(
                technology=technology.lower(),
                base_url=config["url"],
                max_pages=max_pages,
                delay=delay
            )
        
        if result.get("errors"):
            click.echo(f"Warnings during scraping: {len(result['errors'])} errors encountered")
        
        click.echo(f"Scraped {result.get('total_pages', 0)} pages for {technology}")
        
    else:
        # Scrape all technologies
        click.echo("Scraping documentation for all supported technologies...")
        click.echo("This may take a while. Be patient and respectful of rate limits.")
        
        results = scraper.scrape_all_technologies()
        
        total_pages = sum(r.get('total_pages', 0) for r in results.values() if isinstance(r, dict))
        total_errors = sum(len(r.get('errors', [])) for r in results.values() if isinstance(r, dict))
        
        click.echo(f"\nScraping completed!")
        click.echo(f"Total pages scraped: {total_pages}")
        click.echo(f"Total errors encountered: {total_errors}")
        click.echo(f"Data saved to: {output_dir}")

@cli.command()
@click.option('--input-dir', default='training_data', help='Directory containing scraped documentation')
@click.option('--output-file', default='training_dataset.jsonl', help='Output file for training dataset')
@click.option('--technology', help='Filter by specific technology')
def create_dataset(input_dir, output_file, technology):
    """Create training dataset from scraped documentation.
    
    This command processes scraped documentation and creates a training dataset
    suitable for fine-tuning language models.
    """
    if not os.path.exists(input_dir):
        click.echo(f"Error: Input directory '{input_dir}' does not exist.")
        click.echo("Run 'scrape-docs' first to gather documentation.")
        return
    
    click.echo(f"Creating training dataset from {input_dir}...")
    
    training_entries = []
    
    # Process scraped documentation files
    for filename in os.listdir(input_dir):
        if filename.endswith('_docs.json'):
            tech = filename.replace('_docs.json', '')
            
            if technology and tech != technology:
                continue
            
            filepath = os.path.join(input_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    scraped_data = json.load(f)
                
                # Create training dataset from scraped data
                scraper = DocumentationScraper()
                tech_training_data = scraper.create_training_dataset(tech, scraped_data)
                training_entries.extend(tech_training_data)
                
                click.echo(f"Processed {tech}: {len(tech_training_data)} training entries")
                
            except Exception as e:
                click.echo(f"Error processing {filename}: {str(e)}")
    
    # Save combined training dataset
    output_path = os.path.join(input_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in training_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    click.echo(f"Training dataset created: {output_path}")
    click.echo(f"Total training entries: {len(training_entries)}")

@cli.command()
@click.option('--technology', help='Technology to show supported features for')
def list_technologies(technology):
    """List supported technologies and their features."""
    from .llm.training_prompts import OFFICIAL_DOCS
    
    if technology:
        if technology.lower() not in OFFICIAL_DOCS:
            click.echo(f"Error: Unsupported technology '{technology}'. Supported: {', '.join(OFFICIAL_DOCS.keys())}")
            return
        
        config = OFFICIAL_DOCS[technology.lower()]
        click.echo(f"\n{technology.upper()} Support:")
        click.echo(f"  Documentation URL: {config['url']}")
        if 'source' in config:
            click.echo(f"  Source Code: {config['source']}")
        if 'focus' in config:
            click.echo(f"  Focus Areas: {', '.join(config['focus'])}")
    else:
        click.echo("Supported Technologies:")
        for tech, config in OFFICIAL_DOCS.items():
            click.echo(f"  {tech.upper()}: {config['url']}")

@cli.group()
def llm():
    """Manage LLM providers and credentials."""
    pass

@llm.command()
def list_providers():
    """List available LLM providers and their status."""
    from .llm.unified_client import get_llm_client
    
    client = get_llm_client()
    providers = client.get_available_providers()
    
    click.echo("Available LLM Providers:")
    click.echo("=" * 50)
    
    for provider, available in providers.items():
        status = "✅ Available" if available else "❌ Not configured"
        click.echo(f"  {provider.upper()}: {status}")
    
    click.echo(f"\nCurrent provider: {client.provider.upper()}")

@llm.command()
@click.option('--provider', type=click.Choice(['ollama', 'google_code_assist', 'gemini_cli']), 
              help='LLM provider to set up')
def setup_provider(provider):
    """Set up credentials for an LLM provider."""
    from .llm.unified_client import get_llm_client
    
    client = get_llm_client()
    
    if provider:
        success = client.setup_provider(provider)
        if success:
            click.echo(f"✅ Successfully set up {provider}")
        else:
            click.echo(f"❌ Failed to set up {provider}")
    else:
        # Interactive setup
        click.echo("Available providers:")
        click.echo("  1. ollama - Local Ollama server")
        click.echo("  2. google_code_assist - Google Code Assist API")
        click.echo("  3. gemini_cli - Gemini CLI")
        
        choice = click.prompt("Select provider to set up", type=int, default=1)
        
        provider_map = {
            1: "ollama",
            2: "google_code_assist", 
            3: "gemini_cli"
        }
        
        if choice in provider_map:
            selected_provider = provider_map[choice]
            success = client.setup_provider(selected_provider)
            if success:
                click.echo(f"✅ Successfully set up {selected_provider}")
            else:
                click.echo(f"❌ Failed to set up {selected_provider}")
        else:
            click.echo("Invalid choice")

@llm.command()
@click.option('--provider', type=click.Choice(['ollama', 'google_code_assist', 'gemini_cli']), 
              help='LLM provider to test')
def test_connection(provider):
    """Test connection to an LLM provider."""
    from .llm.unified_client import get_llm_client
    
    client = get_llm_client()
    
    if provider:
        # Test specific provider
        if client.switch_provider(provider):
            success = client.test_connection()
            if success:
                click.echo(f"✅ Connection to {provider} successful")
            else:
                click.echo(f"❌ Connection to {provider} failed")
        else:
            click.echo(f"❌ Failed to switch to {provider}")
    else:
        # Test current provider
        success = client.test_connection()
        if success:
            click.echo(f"✅ Connection to {client.provider} successful")
        else:
            click.echo(f"❌ Connection to {client.provider} failed")

@llm.command()
@click.option('--provider', type=click.Choice(['ollama', 'google_code_assist', 'gemini_cli']), 
              required=True, help='LLM provider to switch to')
def switch_provider(provider):
    """Switch to a different LLM provider."""
    from .llm.unified_client import get_llm_client
    
    client = get_llm_client()
    
    if client.switch_provider(provider):
        click.echo(f"✅ Switched to {provider}")
    else:
        click.echo(f"❌ Failed to switch to {provider}")

@llm.command()
@click.option('--provider', type=click.Choice(['ollama', 'google_code_assist', 'gemini_cli']), 
              help='LLM provider to remove credentials for')
@click.option('--all', 'remove_all', is_flag=True, help='Remove all credentials')
def remove_credentials(provider, remove_all):
    """Remove stored credentials for LLM providers."""
    from .llm.credential_manager import get_credential_manager
    
    credential_manager = get_credential_manager()
    
    if remove_all:
        credential_manager.clear_all_credentials()
        click.echo("✅ All credentials removed")
    elif provider:
        # Remove specific provider credentials
        if provider == "ollama":
            credential_manager.remove_credential(provider, "host")
            credential_manager.remove_credential(provider, "port")
            credential_manager.remove_credential(provider, "model")
        else:
            credential_manager.remove_credential(provider, "api_key")
            if provider == "google_code_assist":
                credential_manager.remove_credential(provider, "project_id")
        
        click.echo(f"✅ Credentials for {provider} removed")
    else:
        click.echo("Please specify --provider or --all")

@cli.command()
@click.option('--provider', type=click.Choice(['ollama', 'google_code_assist', 'gemini_cli']), 
              help='LLM provider to use for the review')
def review_with_provider(provider):
    """Review with a specific LLM provider (alias for review command with provider selection)."""
    # This is just an alias for the review command with provider selection
    # The actual provider selection is handled in the review function
    click.echo(f"Use 'review' command with --provider={provider} option")

if __name__ == "__main__":
    cli() 