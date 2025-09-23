# 🚀 Infrastructure as Code with Terraform & Ansible

This project demonstrates **end-to-end automation** for provisioning and configuring a web server on AWS:

- **Terraform** provisions an AWS EC2 instance and security group.
- **Ansible** configures the server, installs Nginx, and deploys a sample HTML page.
- Demonstrates **Infrastructure as Code (IaC)**, **Configuration Management**, and **DevOps automation**.

---

## 📐 Architecture

Developer → Terraform → AWS EC2 → Ansible → Nginx Web Server → Browser


> You can replace this ASCII diagram with a PNG/SVG diagram for visual clarity.

---

## 🗂️ Project Structure

devops-terraform-ansible/
├── app/
│ └── index.html # Sample web page
├── ansible/
│ ├── playbook.yml # Ansible playbook to configure server
│ └── hosts.ini # Inventory file with EC2 IP
├── terraform/
│ ├── main.tf # Terraform EC2 and Security Group resources
│ ├── variables.tf # Terraform variables
│ ├── outputs.tf # Terraform outputs (EC2 IP/DNS)
│ └── userdata.sh # Userdata script to prepare instance
└── README.md # Project documentation


---

## ⚙️ Prerequisites

- AWS account with IAM credentials
- Terraform installed locally
- Ansible installed locally
- SSH keypair (public & private) for EC2 access

---

## 🚀 Setup & Execution

### 1. Provision Infrastructure with Terraform

```bash
cd terraform
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY

terraform init
terraform apply

Copy the ec2_public_ip from Terraform outputs.



2. Configure Ansible Inventory

Edit ansible/hosts.ini:
[webservers]
<EC2_PUBLIC_IP> ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa


3. Run Ansible Playbook
cd ansible
ansible-playbook -i hosts.ini playbook.yml


Installs Nginx, starts the service, and deploys the sample HTML page.



4. Verify Deployment

Open browser at http://<EC2_PUBLIC_IP>
You should see:
Hello! This server is provisioned with Terraform and configured with Ansible.



5. Tear Down (Optional)
cd terraform
terraform destroy


Removes EC2 instance and security group to avoid extra costs.



Tech Stack

Terraform (Infrastructure as Code
Ansible (Configuration Management)
AWS EC2 (Cloud infrastructure)
Nginx (Web server)
HTML (Sample web page deployment)