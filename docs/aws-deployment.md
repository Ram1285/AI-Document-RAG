# AWS Deployment Guide

This project intentionally avoids Kubernetes, Terraform, and microservices.

## Stage 11: S3

Create a private S3 bucket for uploaded documents.

Environment variables:

```text
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
```

## Stage 12: EC2

Use one small Ubuntu EC2 instance for the Dockerized API.

Install Docker:

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu
```

Run the app:

```bash
docker run -d --name rag-api --env-file .env -p 8000:8000 your-image
```

## Stage 13: RDS PostgreSQL

Create a PostgreSQL RDS instance and set:

```text
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@RDS_ENDPOINT:5432/DB_NAME
```

## Stage 14: IAM

Attach an EC2 instance role with least-privilege access to the S3 bucket and CloudWatch logs.

Minimum S3 permissions:

```json
{
  "Effect": "Allow",
  "Action": ["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
  "Resource": [
    "arn:aws:s3:::YOUR_BUCKET",
    "arn:aws:s3:::YOUR_BUCKET/*"
  ]
}
```

## Stage 15: ECR

Create an ECR repository, then build and push your Docker image from GitHub Actions or locally.

## Stage 16: CloudWatch

Use the EC2 instance role and Docker `awslogs` logging driver, or install the CloudWatch agent.

## Stage 17: GitHub Actions

The included workflow runs tests on pull requests and pushes. Add AWS secrets only when you are ready to push to ECR.

## Stage 18: Security

- Keep `.env` out of Git.
- Use IAM roles instead of hardcoded AWS keys on EC2.
- Set `APP_API_KEY` for simple bearer-token protection.
- Put Nginx or an AWS load balancer in front of EC2 for HTTPS.
