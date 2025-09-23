variable "aws_region" {
  default = "ap-south-1"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "key_name" {
  description = "Existing AWS key pair name"
}

variable "public_key_path" {
  description = "Path to your public SSH key"
}

variable "project_name" {
  default = "terraform-ansible-demo"
}
