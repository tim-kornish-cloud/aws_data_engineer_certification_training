# Data source to fetch the default VPC (replace with your specific VPC if needed)
data "aws_vpc" "default" {
  default = true
}

# Data source to fetch subnets in the default VPC (replace with your specific subnets if needed)
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Create a DB subnet group
resource "aws_db_subnet_group" "default" {
  name       = "main-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "Main DB subnet group"
  }
}

# Security group to allow access to the RDS instance on port 5432
resource "aws_security_group" "rds_sg" {
  name        = "rds_security_group"
  description = "Allow inbound traffic to RDS instance"
  vpc_id      = data.aws_vpc.default.id

  # Example ingress rule: adjust cidr_blocks to your specific IP range or EC2 security group ID
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # WARNING: In a production environment, restrict this to known IPs or other security groups.
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
