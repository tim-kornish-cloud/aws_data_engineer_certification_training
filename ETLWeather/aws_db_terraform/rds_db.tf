# Create the RDS PostgreSQL DB instance
resource "aws_db_instance" "postgres_instance" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "16" # Check the AWS documentation for supported versions
  instance_class         = "db.t3.micro" # Use a free tier eligible instance class if applicable
  identifier             = "my-postgres-db"
  db_name                = var.database
  username               = var.username
  password               = var.password
  parameter_group_name   = "default.postgres16"
  db_subnet_group_name   = aws_db_subnet_group.default.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true # Set to false in production to prevent data loss

  tags = {
    Name = "MyPostgresInstance"
  }
}

# Output the RDS endpoint to connect to the database
output "rds_endpoint" {
  value = aws_db_instance.postgres_instance.endpoint
}
