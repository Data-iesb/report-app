# Big Data IESB - Report Applications

[![Deploy to EKS](https://github.com/Data-iesb/report-app/actions/workflows/deploy.yml/badge.svg)](https://github.com/Data-iesb/report-app/actions/workflows/deploy.yml)

**Author**: Roberto Moreira Diniz  
**GitHub**: [github.com/s33ding](https://www.github.com/s33ding/)  
**LinkedIn**: [linkedin.com/in/s33ding](https://linkedin.com/in/s33ding)

This repository contains the **Streamlit dashboard applications** for the Big Data IESB Platform. These interactive analytics dashboards are deployed on an **Amazon EKS (Elastic Kubernetes Service)** cluster, providing dynamic visualization of academic panels and indicators in a unified interface.

## Platform Integration

This repository is part of the larger **Big Data IESB Project** ecosystem:

- **[Data-IESB](https://github.com/Data-iesb/Data-IESB)** - Main institutional website and platform documentation
- **report-app** (this repo) - Streamlit dashboard applications

## Application Access

- **Reports Dashboard**: https://app.dataiesb.com/report/
- **Development Environment**: Available through EKS cluster endpoints

## Technology Stack

### Application Framework
- **Streamlit**: Interactive dashboard framework
- **Python**: Core programming language
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations

### Infrastructure
- **Amazon EKS**: Kubernetes cluster for container orchestration
- **Docker**: Application containerization
- **Amazon ECR**: Container registry
- **Amazon S3**: Data storage integration
- **Amazon RDS**: Database connectivity

### CI/CD Pipeline
- **GitHub Actions**: Automated deployment workflows
- **AWS CodeBuild**: Container build process
- **Kubernetes**: Pod deployment and management

## Architecture

The Streamlit applications are deployed as containerized pods within the EKS cluster, providing:

- **Scalability**: Automatic scaling based on demand
- **High Availability**: Multi-pod deployment with load balancing
- **Data Integration**: Direct connectivity to S3 and RDS data sources
- **Security**: Integrated with AWS IAM and VPC security

## Repository Structure

```
report-app/
├── apps/                        # Streamlit applications
│   ├── dashboard1/             # Individual dashboard apps
│   ├── dashboard2/
│   └── dashboard3/
├── shared/                     # Shared utilities and components
│   ├── utils.py               # Common functions
│   ├── config.py              # Configuration management
│   └── data_sources.py        # Data connection utilities
├── eks/                       # Kubernetes manifests
│   ├── deployment.yaml        # Application deployment
│   ├── service.yaml          # Load balancer service
│   └── configmap.yaml        # Configuration maps
├── iaac/                      # Infrastructure as Code
│   ├── dynamodb.sh           # DynamoDB table creation
│   └── make-public.sh        # S3 bucket configuration
├── Dockerfile                 # Container definition
├── requirements.txt           # Python dependencies
└── buildspec.yml             # AWS CodeBuild configuration
```

## Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/Data-iesb/report-app.git
cd report-app

# Install dependencies
pip install -r requirements.txt

# Run specific dashboard
streamlit run apps/dashboard1/app.py
```

### Docker Development
```bash
# Build container
docker build -t report-app .

# Run container
docker run -p 8501:8501 report-app
```

## Deployment

### Automatic Deployment
Changes pushed to the main branch trigger automatic deployment to the EKS cluster via GitHub Actions.

### Manual Deployment
```bash
# Build and push to ECR
docker build -t report-app .
docker tag report-app:latest <ecr-repo-url>:latest
docker push <ecr-repo-url>:latest

# Deploy to EKS
kubectl apply -f eks/
```

## Data Sources

The applications integrate with multiple data sources:

- **Amazon S3**: Static data files and reports
- **Amazon RDS**: Structured database queries
- **DynamoDB**: NoSQL data for team information and metadata
- **External APIs**: Public data sources when applicable

## Dashboard Applications

### Academic Indicators
- Student performance metrics
- Research output analytics
- Institutional KPIs

### Public Data Analytics
- Government transparency indicators
- Social development metrics
- Economic performance dashboards

### Interactive Reports
- Dynamic filtering and visualization
- Export capabilities
- Real-time data updates

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-dashboard`
3. Develop and test locally
4. Commit changes with clear messages
5. Push to your fork
6. Create Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Use type hints where applicable
- Include docstrings for functions
- Test dashboards locally before committing

## Infrastructure Management

### EKS Cluster Configuration
- **Cluster Name**: `sas-6881323-eks`
- **Node Groups**: Auto-scaling based on demand
- **Service Account**: Configured with appropriate IAM permissions

### Data Access Policies
- S3 bucket access for data retrieval
- RDS connection permissions
- DynamoDB read/write access

## About IESB

**Centro Universitário IESB** is committed to fostering innovation in education and research. These dashboard applications serve as practical learning environments where students and researchers can apply Data Science and Artificial Intelligence methodologies to real-world scenarios, contributing to evidence-based decision making and social development.

---

*This application suite is maintained by Centro Universitário IESB for educational, research, and public service purposes.*
