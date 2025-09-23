# 🚀 Flask CI/CD with Docker, GitHub Actions & Terraform on AWS EC2

This project demonstrates an **automated CI/CD pipeline** for a simple Flask web application:

- **Flask app** → containerized with **Docker**
- **GitHub Actions** builds & pushes the image to **Docker Hub**
- **Terraform** provisions an **AWS EC2** instance with Docker pre-installed
- **Deploy script** automatically runs the latest image on EC2 on every push to the `main` branch

---

## 📐 Architecture

Developer Push → GitHub Actions → Docker Hub → AWS EC2 (Terraform-provisioned)
| |
└──── deploy.sh ──┘


> You can replace this ASCII diagram with a proper PNG or SVG diagram for more visual appeal.

---

## 🗂️ Project Structure

devops-cicd-flask/
├── app.py # Flask application
├── requirements.txt # Python dependencies
├── Dockerfile # Container definition
├── deploy.sh # Script run on EC2 to deploy latest Docker image
├── .github/workflows/ci-cd.yml # GitHub Actions pipeline
└── terraform/ # Terraform code to provision EC2 instance
├── main.tf
├── variables.tf
├── outputs.tf
└── ec2-userdata.sh



---

## ⚙️ Prerequisites

- AWS account with IAM credentials
- Terraform installed locally
- Docker Hub account & access token
- GitHub repository for this code
- SSH keypair (public & private) for EC2

---

## 🚀 Setup & Execution

### 1. Provision Infrastructure with Terraform

```bash
cd terraform
# export your AWS credentials
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY

terraform init
terraform apply


2. Configure GitHub Secrets

Repository → Settings → Secrets and variables → Actions:

Secret	Value
DOCKERHUB_USERNAME	your Docker Hub username
DOCKERHUB_TOKEN	Docker Hub access token
EC2_HOST	EC2 public IP from Terraform output
EC2_SSH_KEY	contents of your private SSH key


3. Push Code to GitHub
git add .
git commit -m "Initial CI/CD project"
git push origin main

4. Watch Pipeline Run

Go to GitHub → Actions tab

Observe build, push, and deploy steps executing automatically

5. Verify Deployment

Open a browser at http://<EC2_PUBLIC_IP>:
Hello from my automated CI/CD Flask App!


🧰 Tech Stack

Flask (Python web framework)

Docker (containerization)

GitHub Actions (CI/CD automation)

Terraform (infrastructure as code)

AWS EC2 (cloud deployment)

Docker Hub (image registry)
