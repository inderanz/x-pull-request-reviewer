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
from agent.main import review_pr_or_branch
from llm.doc_scraper import DocumentationScraper, create_sample_training_data
import json
import os

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
def review(pr, repo, branch, pr_number, repo_slug, no_interactive):
    """Review a pull request or branch. Optionally post LLM review as PR comment if --pr-number and --repo-slug are provided.
    
    The review now includes interactive change management where you can:
    - Apply specific suggested changes
    - Revert applied changes if needed
    - Selectively ignore certain recommendations
    """
    interactive = not no_interactive
    review_pr_or_branch(
        repo_url=pr, 
        repo_path=repo, 
        branch=branch, 
        pr_number=pr_number, 
        repo_slug=repo_slug,
        interactive=interactive
    )

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
            from llm.training_prompts import OFFICIAL_DOCS
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
            from llm.training_prompts import OFFICIAL_DOCS
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
    from llm.training_prompts import OFFICIAL_DOCS
    
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

if __name__ == "__main__":
    cli() 