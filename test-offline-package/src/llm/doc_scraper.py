"""
Documentation Scraper for x-pull-request-reviewer
Helps gather content from official documentation sites for training purposes.
"""

import requests
import json
import os
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re


class DocumentationScraper:
    """Scraper for official documentation sites."""
    
    def __init__(self, output_dir: str = "training_data"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def scrape_technology_docs(self, technology: str, base_url: str, 
                              max_pages: int = 50, delay: float = 1.0) -> Dict:
        """
        Scrape documentation for a specific technology.
        
        Args:
            technology: Name of the technology (e.g., 'go', 'python')
            base_url: Base URL of the documentation
            max_pages: Maximum number of pages to scrape
            delay: Delay between requests in seconds
        
        Returns:
            Dictionary containing scraped content
        """
        print(f"Scraping documentation for {technology.upper()} from {base_url}")
        
        scraped_data = {
            "technology": technology,
            "base_url": base_url,
            "pages": [],
            "total_pages": 0,
            "errors": []
        }
        
        try:
            # Get the main page
            response = self.session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find documentation links
            doc_links = self._find_doc_links(soup, base_url)
            
            print(f"Found {len(doc_links)} potential documentation pages")
            
            # Scrape each page
            for i, link in enumerate(doc_links[:max_pages]):
                try:
                    print(f"Scraping page {i+1}/{min(len(doc_links), max_pages)}: {link}")
                    
                    page_data = self._scrape_page(link)
                    if page_data:
                        scraped_data["pages"].append(page_data)
                    
                    # Respect rate limits
                    time.sleep(delay)
                    
                except Exception as e:
                    error_msg = f"Error scraping {link}: {str(e)}"
                    print(error_msg)
                    scraped_data["errors"].append(error_msg)
            
            scraped_data["total_pages"] = len(scraped_data["pages"])
            
            # Save to file
            output_file = os.path.join(self.output_dir, f"{technology}_docs.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, indent=2, ensure_ascii=False)
            
            print(f"Scraped {scraped_data['total_pages']} pages for {technology}")
            print(f"Data saved to {output_file}")
            
            return scraped_data
            
        except Exception as e:
            print(f"Error scraping {technology} documentation: {str(e)}")
            scraped_data["errors"].append(str(e))
            return scraped_data
    
    def _find_doc_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find documentation links from the main page."""
        links = []
        
        # Technology-specific link patterns
        if "docs.python.org" in base_url:
            # Python-specific patterns
            link_patterns = [
                'a[href*="/tutorial/"]',
                'a[href*="/library/"]',
                'a[href*="/reference/"]',
                'a[href*="/howto/"]',
                'a[href*="/distributing/"]',
                'a[href*="/extending/"]',
                'a[href*="/c-api/"]',
                'a[href*="/faq/"]',
                'a[href*="/whatsnew/"]',
                'a[href*="/glossary/"]',
                'a[href*="/install/"]',
                'a[href*="/using/"]',
                'a[href*="tutorial/"]',
                'a[href*="library/"]',
                'a[href*="reference/"]',
                'a[href*="howto/"]',
                'a[href*="distributing/"]',
                'a[href*="extending/"]',
                'a[href*="c-api/"]',
                'a[href*="faq/"]',
                'a[href*="whatsnew/"]',
                'a[href*="glossary/"]',
                'a[href*="install/"]',
                'a[href*="using/"]'
            ]
        elif "golang.org" in base_url:
            # Go-specific patterns
            link_patterns = [
                'a[href*="/doc/"]',
                'a[href*="/pkg/"]',
                'a[href*="/cmd/"]',
                'a[href*="/tutorial/"]',
                'a[href*="/ref/"]'
            ]
        elif "kubernetes.io" in base_url:
            # Kubernetes-specific patterns
            link_patterns = [
                'a[href*="/docs/"]',
                'a[href*="/concepts/"]',
                'a[href*="/tasks/"]',
                'a[href*="/reference/"]',
                'a[href*="/setup/"]'
            ]
        elif "helm.sh" in base_url:
            # Helm-specific patterns
            link_patterns = [
                'a[href*="/docs/"]',
                'a[href*="/charts/"]',
                'a[href*="/tutorial/"]'
            ]
        elif "terraform.io" in base_url:
            # Terraform-specific patterns
            link_patterns = [
                'a[href*="/docs/"]',
                'a[href*="/language/"]',
                'a[href*="/providers/"]',
                'a[href*="docs/"]',
                'a[href*="language/"]',
                'a[href*="providers/"]'
            ]
        elif "registry.terraform.io" in base_url:
            # Terraform Registry provider patterns
            link_patterns = [
                'a[href*="/docs/"]',
                'a[href*="/guides/"]',
                'a[href*="/examples/"]',
                'a[href*="docs/"]',
                'a[href*="guides/"]',
                'a[href*="examples/"]'
            ]
        else:
            # Generic patterns for other technologies
            link_patterns = [
                'a[href*="/doc/"]',
                'a[href*="/docs/"]',
                'a[href*="/guide/"]',
                'a[href*="/tutorial/"]',
                'a[href*="/reference/"]',
                'a[href*="/api/"]',
                'a[href*="/examples/"]',
                'a[href*="/best-practices/"]',
                'a[href*="/security/"]',
                'a[href*="/performance/"]'
            ]
        
        for pattern in link_patterns:
            elements = soup.select(pattern)
            for element in elements:
                href = element.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    # Filter out external links and non-documentation pages
                    if (full_url.startswith(base_url) and 
                        full_url not in links and
                        not any(exclude in full_url for exclude in ['#', 'javascript:', 'mailto:', 'tel:'])):
                        links.append(full_url)
        
        return links
    
    def _scrape_page(self, url: str) -> Optional[Dict]:
        """Scrape content from a single page."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract code examples
            code_examples = self._extract_code_examples(soup)
            
            # Extract headings for structure
            headings = self._extract_headings(soup)
            
            return {
                "url": url,
                "title": title_text,
                "content": content,
                "code_examples": code_examples,
                "headings": headings,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error scraping page {url}: {str(e)}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        # Common selectors for main content
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.documentation',
            '.doc-content',
            '#content',
            '#main',
            '.post-content',
            '.entry-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove script and style elements
                for script in element(["script", "style"]):
                    script.decompose()
                
                return element.get_text(separator='\n', strip=True)
        
        # Fallback: get body content
        body = soup.find('body')
        if body:
            for script in body(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            return body.get_text(separator='\n', strip=True)
        
        return ""
    
    def _extract_code_examples(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract code examples from the page."""
        code_examples = []
        
        # Find code blocks
        code_blocks = soup.find_all(['pre', 'code'])
        
        for block in code_blocks:
            # Skip if it's inside a script tag
            if block.find_parent('script'):
                continue
            
            code_text = block.get_text(strip=True)
            if len(code_text) > 10:  # Only include substantial code blocks
                language = block.get('class', [''])[0] if block.get('class') else ''
                
                code_examples.append({
                    "language": language,
                    "code": code_text,
                    "element": str(block)[:200] + "..." if len(str(block)) > 200 else str(block)
                })
        
        return code_examples
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract headings for document structure."""
        headings = []
        
        for i in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    "level": i,
                    "text": heading.get_text(strip=True),
                    "id": heading.get('id', '')
                })
        
        return headings
    
    def create_training_dataset(self, technology: str, scraped_data: Dict) -> List[Dict]:
        """Create training dataset from scraped documentation."""
        from .training_prompts import create_training_dataset_entry
        
        training_data = []
        
        for page in scraped_data.get("pages", []):
            # Create documentation ingestion entry
            doc_entry = create_training_dataset_entry(
                technology=technology,
                doc_content=page.get("content", ""),
                code_example=page.get("code_examples", [])
            )
            training_data.append(doc_entry)
            
            # Create code review entries for code examples
            for code_example in page.get("code_examples", []):
                if code_example.get("code"):
                    # This would be enhanced with actual code review prompts
                    pass
        
        return training_data
    
    def scrape_all_technologies(self) -> Dict:
        """Scrape documentation for all supported technologies."""
        from .training_prompts import OFFICIAL_DOCS
        
        results = {}
        
        for tech, config in OFFICIAL_DOCS.items():
            print(f"\n{'='*50}")
            print(f"Scraping {tech.upper()} documentation")
            print(f"{'='*50}")
            
            try:
                result = self.scrape_technology_docs(
                    technology=tech,
                    base_url=config["url"],
                    max_pages=30,  # Conservative limit
                    delay=2.0  # Be respectful to servers
                )
                results[tech] = result
                
                # Create training dataset
                training_data = self.create_training_dataset(tech, result)
                
                # Save training data
                training_file = os.path.join(self.output_dir, f"{tech}_training.jsonl")
                with open(training_file, 'w', encoding='utf-8') as f:
                    for entry in training_data:
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                
                print(f"Training data saved to {training_file}")
                
            except Exception as e:
                print(f"Error scraping {tech}: {str(e)}")
                results[tech] = {"error": str(e)}
        
        return results
    
    def scrape_terraform_provider_docs(self, provider_name: str, base_url: str, 
                                      max_pages: int = 30, delay: float = 1.0) -> Dict:
        """
        Special scraper for Terraform provider documentation from registry.
        
        Args:
            provider_name: Name of the provider (e.g., 'aws', 'kubernetes', 'google')
            base_url: Base URL of the provider documentation
            max_pages: Maximum number of pages to scrape
            delay: Delay between requests in seconds
        
        Returns:
            Dictionary containing scraped content
        """
        print(f"Scraping Terraform {provider_name.upper()} provider documentation from {base_url}")
        
        scraped_data = {
            "technology": f"terraform-{provider_name}",
            "base_url": base_url,
            "pages": [],
            "total_pages": 0,
            "errors": []
        }
        
        try:
            # Get the main provider page
            response = self.session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # For Terraform registry, look for resource documentation links
            resource_links = []
            
            # Common patterns for Terraform provider docs
            link_patterns = [
                'a[href*="/docs/resources/"]',
                'a[href*="/docs/data-sources/"]',
                'a[href*="/docs/guides/"]',
                'a[href*="resources/"]',
                'a[href*="data-sources/"]',
                'a[href*="guides/"]'
            ]
            
            for pattern in link_patterns:
                elements = soup.select(pattern)
                for element in elements:
                    href = element.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if (full_url.startswith(base_url) and 
                            full_url not in resource_links and
                            not any(exclude in full_url for exclude in ['#', 'javascript:', 'mailto:', 'tel:'])):
                            resource_links.append(full_url)
            
            print(f"Found {len(resource_links)} potential documentation pages")
            
            # Scrape each page
            for i, link in enumerate(resource_links[:max_pages]):
                try:
                    print(f"Scraping page {i+1}/{min(len(resource_links), max_pages)}: {link}")
                    
                    page_data = self._scrape_page(link)
                    if page_data:
                        scraped_data["pages"].append(page_data)
                    
                    # Respect rate limits
                    time.sleep(delay)
                    
                except Exception as e:
                    error_msg = f"Error scraping {link}: {str(e)}"
                    print(error_msg)
                    scraped_data["errors"].append(error_msg)
            
            scraped_data["total_pages"] = len(scraped_data["pages"])
            
            # Save to file
            output_file = os.path.join(self.output_dir, f"terraform-{provider_name}_docs.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, indent=2, ensure_ascii=False)
            
            print(f"Scraped {scraped_data['total_pages']} pages for terraform-{provider_name}")
            print(f"Data saved to {output_file}")
            
            return scraped_data
            
        except Exception as e:
            print(f"Error scraping terraform-{provider_name} documentation: {str(e)}")
            scraped_data["errors"].append(str(e))
            return scraped_data


def create_sample_training_data() -> List[Dict]:
    """Create sample training data for testing purposes."""
    sample_data = []
    
    # Sample Go documentation entry
    go_doc = """
    # Go Concurrency Patterns
    
    Go provides goroutines and channels for concurrent programming.
    
    ## Goroutines
    A goroutine is a lightweight thread managed by the Go runtime.
    
    ```go
    go func() {
        fmt.Println("Hello from goroutine")
    }()
    ```
    
    ## Channels
    Channels are typed conduits for communication between goroutines.
    
    ```go
    ch := make(chan string)
    go func() {
        ch <- "Hello"
    }()
    msg := <-ch
    ```
    
    ## Best Practices
    - Always handle errors
    - Use buffered channels when appropriate
    - Avoid goroutine leaks
    """
    
    sample_data.append({
        "prompt": f"You are learning from the official documentation of GO. Start by understanding the core concepts from this content.\n\nDOC START:\n{go_doc}\nDOC END\n\nBased on this official documentation, please:\n\n1. **Summarize Key Points**: Extract the main concepts, features, and capabilities\n2. **List Tools/APIs**: Identify any command-line tools, APIs, or interfaces mentioned\n3. **Highlight Best Practices**: Note any recommended practices, patterns, or guidelines\n4. **Identify Warnings**: Capture any warnings, limitations, or common pitfalls\n5. **Extract Examples**: Note any code examples or configuration samples\n6. **Security Considerations**: Identify any security-related information\n7. **Performance Notes**: Capture any performance considerations or optimizations\n\nFormat your response as structured markdown with clear sections.",
        "response": """Based on the GO official documentation:

## Key Points Summary
- Go provides goroutines for lightweight concurrent programming
- Channels enable communication between goroutines
- Concurrency is built into the language design

## Tools and APIs
- `go` keyword for starting goroutines
- `make(chan Type)` for creating channels
- Channel operators `<-` for sending/receiving

## Best Practices
- Always handle errors properly
- Use buffered channels when appropriate
- Avoid goroutine leaks by ensuring proper cleanup

## Warnings and Limitations
- Goroutines can leak if not properly managed
- Unbuffered channels can cause deadlocks
- Need to handle channel closing properly

## Security Considerations
- Concurrent access to shared data needs synchronization
- Use mutexes or channels for thread-safe operations

## Performance Notes
- Goroutines are lightweight (2KB stack initially)
- Channels provide efficient communication
- Buffered channels can improve performance for bursty workloads""",
        "technology": "go",
        "type": "documentation_ingestion"
    })
    
    return sample_data


def main():
    """Main function for running the scraper."""
    scraper = DocumentationScraper()
    
    # Create sample training data
    print("Creating sample training data...")
    sample_data = create_sample_training_data()
    
    sample_file = os.path.join(scraper.output_dir, "sample_training.jsonl")
    with open(sample_file, 'w', encoding='utf-8') as f:
        for entry in sample_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"Sample training data saved to {sample_file}")
    
    # Uncomment to scrape actual documentation (be respectful of rate limits)
    # results = scraper.scrape_all_technologies()
    # print("Scraping completed!")


if __name__ == "__main__":
    main() 