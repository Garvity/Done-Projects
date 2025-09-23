#!/bin/bash
# Update packages
apt-get update -y
apt-get install -y docker.io

# Enable Docker
systemctl enable docker
systemctl start docker

# Create deploy.sh placeholder
cat << 'EOF' > /home/ubuntu/deploy.sh
#!/bin/bash
APP_NAME="flaskapp"
DOCKER_IMAGE="yourdockerhubusername/flaskapp:latest"
docker rm -f $APP_NAME || true
docker pull $DOCKER_IMAGE
docker run -d --name $APP_NAME -p 80:5000 $DOCKER_IMAGE
EOF

chmod +x /home/ubuntu/deploy.sh
chown ubuntu:ubuntu /home/ubuntu/deploy.sh
