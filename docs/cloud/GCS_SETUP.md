# Google Cloud Storage Setup Guide

This guide provides complete instructions for setting up Google Cloud Storage (GCS) for AIAlchemy.

## Table of Contents
- [Quick Setup](#quick-setup)
- [Manual Setup Steps](#manual-setup-steps)
- [Permissions Configuration](#permissions-configuration)
- [Troubleshooting](#troubleshooting)

## Quick Setup

Run the automated setup script:

```bash
# Validate and setup GCS configuration
python3 setup-gcs-complete.py
```

## Manual Setup Steps

If you need to set up GCS manually:

1. Set your project ID:
```bash
export PROJECT_ID="your-gcp-project-id"
```

2. Create service account:
```bash
gcloud iam service-accounts create aialchemy-storage \
    --display-name="AIAlchemy Storage Service Account"
```

[Content merged from GCS_SETUP_COMMANDS.md and COMPLETE_GCS_SETUP.md...]

## Permissions Configuration

To ensure proper access:

1. Grant storage permissions:
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

[Content merged from FIX_GCS_PERMISSIONS.md...]

## Troubleshooting

Common GCS issues and solutions:

1. Permission Denied Errors
2. Bucket Access Issues
3. Service Account Key Problems

[Additional content merged from other GCS documentation...]