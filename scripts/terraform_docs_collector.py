#!/usr/bin/env python3
"""
Terraform Documentation Collector
Collects Terraform documentation from multiple sources for training.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List
import time

class TerraformDocsCollector:
    """Collect Terraform documentation from multiple sources."""
    
    def __init__(self, output_dir: str = "training_data"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def collect_terraform_core_docs(self) -> Dict:
        """Collect core Terraform documentation."""
        print("Collecting core Terraform documentation...")
        
        # Core Terraform documentation URLs
        core_urls = [
            "https://developer.hashicorp.com/terraform/language",
            "https://developer.hashicorp.com/terraform/language/syntax",
            "https://developer.hashicorp.com/terraform/language/modules",
            "https://developer.hashicorp.com/terraform/language/values",
            "https://developer.hashicorp.com/terraform/language/state",
            "https://developer.hashicorp.com/terraform/language/resources",
            "https://developer.hashicorp.com/terraform/language/data-sources",
            "https://developer.hashicorp.com/terraform/language/functions",
            "https://developer.hashicorp.com/terraform/language/expressions",
            "https://developer.hashicorp.com/terraform/language/blocks"
        ]
        
        collected_data = {
            "technology": "terraform-core",
            "source": "developer.hashicorp.com",
            "pages": [],
            "total_pages": 0
        }
        
        for url in core_urls:
            try:
                print(f"Collecting: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Extract content (simplified for now)
                content = response.text[:5000]  # First 5000 chars for training
                
                collected_data["pages"].append({
                    "url": url,
                    "title": f"Terraform Core - {url.split('/')[-1]}",
                    "content": content,
                    "timestamp": time.time()
                })
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"Error collecting {url}: {e}")
        
        collected_data["total_pages"] = len(collected_data["pages"])
        
        # Save to file
        output_file = os.path.join(self.output_dir, "terraform_core_docs.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, indent=2, ensure_ascii=False)
        
        print(f"Collected {collected_data['total_pages']} core Terraform pages")
        return collected_data
    
    def collect_terraform_examples(self) -> Dict:
        """Collect Terraform examples and best practices."""
        print("Collecting Terraform examples and best practices...")
        
        # Example repositories and documentation
        example_sources = [
            {
                "name": "terraform-aws-examples",
                "url": "https://github.com/hashicorp/terraform-aws-vault",
                "description": "AWS Vault deployment examples"
            },
            {
                "name": "terraform-kubernetes-examples", 
                "url": "https://github.com/hashicorp/terraform-provider-kubernetes/tree/main/examples",
                "description": "Kubernetes provider examples"
            },
            {
                "name": "terraform-best-practices",
                "url": "https://developer.hashicorp.com/terraform/tutorials/aws-get-started",
                "description": "AWS getting started tutorial"
            }
        ]
        
        examples_data = {
            "technology": "terraform-examples",
            "source": "multiple",
            "examples": [],
            "total_examples": 0
        }
        
        # For now, create structured examples based on common patterns
        common_examples = [
            {
                "name": "AWS VPC Example",
                "content": """
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  instance_tenancy     = "default"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "public"
  }
}
""",
                "description": "Basic AWS VPC and subnet configuration"
            },
            {
                "name": "Kubernetes Deployment Example",
                "content": """
resource "kubernetes_deployment" "example" {
  metadata {
    name = "terraform-example"
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        app = "MyApp"
      }
    }
    template {
      metadata {
        labels = {
          app = "MyApp"
        }
      }
      spec {
        container {
          image = "nginx:1.21.6"
          name  = "example"
          port {
            container_port = 80
          }
        }
      }
    }
  }
}
""",
                "description": "Basic Kubernetes deployment configuration"
            },
            {
                "name": "Terraform Module Example",
                "content": """
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "3.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}
""",
                "description": "Using Terraform modules for VPC creation"
            }
        ]
        
        examples_data["examples"] = common_examples
        examples_data["total_examples"] = len(common_examples)
        
        # Save to file
        output_file = os.path.join(self.output_dir, "terraform_examples.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(examples_data, f, indent=2, ensure_ascii=False)
        
        print(f"Collected {examples_data['total_examples']} Terraform examples")
        return examples_data
    
    def collect_all_terraform_docs(self) -> Dict:
        """Collect all Terraform documentation from multiple sources."""
        print("=== TERRAFORM DOCUMENTATION COLLECTION ===")
        
        results = {}
        
        # Collect core documentation
        results["core"] = self.collect_terraform_core_docs()
        
        # Collect examples
        results["examples"] = self.collect_terraform_examples()
        
        # Summary
        total_pages = results["core"]["total_pages"]
        total_examples = results["examples"]["total_examples"]
        
        print(f"\n=== COLLECTION SUMMARY ===")
        print(f"Core documentation pages: {total_pages}")
        print(f"Example configurations: {total_examples}")
        print(f"Total Terraform training entries: {total_pages + total_examples}")
        
        return results

def main():
    """Main function to run the Terraform documentation collector."""
    collector = TerraformDocsCollector()
    results = collector.collect_all_terraform_docs()
    
    print("\n✅ Terraform documentation collection completed!")
    print("Files saved to training_data/ directory")

if __name__ == "__main__":
    main() 