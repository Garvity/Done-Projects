output "ec2_public_ip" {
  description = "Public IP of EC2"
  value       = aws_instance.flask.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of EC2"
  value       = aws_instance.flask.public_dns
}
