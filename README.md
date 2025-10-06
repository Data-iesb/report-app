# Big Data IESB - Report Applications

**Author**: Roberto Moreira Diniz  
**GitHub**: [github.com/s33ding](https://www.github.com/s33ding/)  
**LinkedIn**: [linkedin.com/in/s33ding](https://linkedin.com/in/s33ding)

This repository contains the **Streamlit dashboard applications** for the Big Data IESB Platform. These interactive analytics dashboards are deployed on an **Amazon EKS (Elastic Kubernetes Service)** cluster, providing dynamic visualization of academic panels and indicators.

## Platform Integration

This repository is part of the larger **Big Data IESB Project** ecosystem:

- **[Data-IESB](https://github.com/Data-iesb/Data-IESB)** - Main institutional website and platform documentation
- **report-app** (this repo) - Streamlit dashboard applications

## Application Access

- **Reports Dashboard**: https://app.dataiesb.com/report/

## Repository Structure

```
report-app/
├── app/                        # Main Streamlit application
│   ├── app.py                 # Primary dashboard application
│   ├── test_app.py            # Application tests
│   ├── requirements.txt       # Python dependencies
│   ├── style.css             # Custom styling
│   ├── .streamlit/           # Streamlit configuration
│   │   └── config.toml       # App configuration
│   └── tmp/                  # Development files
├── eks/                      # Kubernetes manifests
│   ├── deployment.yaml       # EKS deployment configuration
│   ├── service.yaml         # Load balancer service
│   ├── eksctl-sa.sh         # Service account setup
│   ├── s3-policy-fix.json   # S3 access policies
│   └── s3-policy-updated.json
├── iaac/                     # Infrastructure as Code
│   ├── dynamodb.sh          # DynamoDB table creation
│   └── make-public.sh       # S3 bucket configuration
├── Dockerfile-Local          # Local development container
├── Dockerfile-EKS           # EKS deployment container
├── requirements.txt         # Root dependencies
├── buildspec.yml           # AWS CodeBuild configuration
├── test_dynamodb.py        # DynamoDB connection tests
├── install.sh              # Installation script
├── reinstall.sh            # Reinstallation script
└── uninstall.sh            # Cleanup script
```

## Technology Stack

- **Streamlit**: Interactive dashboard framework
- **Python**: Core programming language
- **Amazon EKS**: Kubernetes cluster for deployment
- **Amazon DynamoDB**: NoSQL database integration
- **Amazon S3**: Data storage and access
- **Docker**: Application containerization

## Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/Data-iesb/report-app.git
cd report-app

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/app.py
```

### Docker Development
```bash
# Build local container
docker build -f Dockerfile-Local -t report-app-local .

# Run container
docker run -p 8501:8501 report-app-local
```

## Deployment

### EKS Deployment
The application is automatically deployed to Amazon EKS cluster `sas-6881323-eks` via AWS CodeBuild when changes are pushed to the main branch.

### Manual Deployment
```bash
# Setup service account
./eks/eksctl-sa.sh

# Deploy to EKS
kubectl apply -f eks/deployment.yaml
kubectl apply -f eks/service.yaml
```

## Infrastructure Management

### DynamoDB Setup
```bash
# Create required DynamoDB tables
./iaac/dynamodb.sh
```

### S3 Configuration
```bash
# Configure S3 bucket permissions
./iaac/make-public.sh
```

### Testing
```bash
# Test DynamoDB connection
python test_dynamodb.py

# Test application
python app/test_app.py
```

## About IESB

**Centro Universitário IESB** is committed to fostering innovation in education and research. This dashboard application serves as a practical learning environment where students and researchers can apply Data Science and Artificial Intelligence methodologies to real-world scenarios.

---

*This application is maintained by Centro Universitário IESB for educational, research, and public service purposes.*
