# Test Terraform file with multiple issues for XPRR testing
# This file contains intentional configuration issues and best practice violations

# Missing description
variable "instance_name" {
  type = string
}

# Missing description
variable "instance_type" {
  type    = string
  default = "t2.micro"
}

# Resource without description
resource "aws_instance" "example" {
  ami           = "ami-12345678"  # Hardcoded AMI
  instance_type = var.instance_type
  
  # Missing tags
  # Missing security groups
  # Missing key pair
  
  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y apache2
              EOF
}

# Resource with missing required fields
resource "aws_security_group" "example" {
  name = "test-sg"
  
  # Missing ingress rules
  # Missing egress rules
}

# Data source without proper filtering
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["amazon"]
  
  # Missing proper filtering
}

# Output without description
output "instance_ip" {
  value = aws_instance.example.public_ip
} 