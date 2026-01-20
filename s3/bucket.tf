provider "aws" {
	region = "us-east-2" # ohio server
}

# set up S3 bucket
resource "aws_s3_bucket" "my_bucket" {
	bucket = var.bucket_name # bucket name using youtube tutorial
	tags = var.tags
}

# Console commands using windows console to use terraform

# 1) ~$ terraform init
# 2) ~$ terraform plan
# 3) ~$ terraform apply
# 4) ~$ yes
# 5) ~$ terraform destroy -auto-approve
