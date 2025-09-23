variable "aws_region" {
  description = "AWS region"
  default     = "ap-south-1" # change to your region
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "key_name" {
  description = "Existing AWS key pair name"
}

variable "public_key_path" {
  description = "Path to your SSH public key"
}

variable "project_name" {
  default = "flask-devops"
}
