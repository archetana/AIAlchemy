# Deployment Guide

Complete guide for deploying AIAlchemy to production environments.

## Table of Contents
- [Deployment Options](#deployment-options)
- [Prerequisites](#prerequisites)
- [GitHub Actions Setup](#github-actions-setup)
- [Manual Deployment Steps](#manual-deployment-steps)
- [Troubleshooting](#troubleshooting)

## Deployment Options

1. **Nginx Gateway (Recommended)**
   - Cost: ~$25/month
   - No domain required
   - Automatic SSL
   ```bash
   ./deploy-nginx-gateway.sh
   ```

2. **Cloud Load Balancer (Enterprise)**
   - Cost: ~$45/month
   - Domain required
   - Global CDN
   ```bash
   DOMAIN_NAME=yourdomain.com ./deploy-gcp.sh
   ```

[Content merged from DEPLOY_YML_MANUAL_UPDATES.md...]

## GitHub Actions Setup

Required repository secrets:
- `GCP_PROJECT_ID`
- `GCP_SA_KEY`
- `DOMAIN_NAME` (optional)

[Content merged from GITHUB_SECRETS_SETUP.md...]

## Supabase Deployment

Steps for deploying with Supabase:
1. Database setup
2. Authentication configuration
3. Environment variables

[Content merged from SUPABASE_DEPLOYMENT.md...]

## Troubleshooting

Common deployment issues and solutions...

[Additional content merged from WORKFLOW_FIX_EXPLANATION.md...]