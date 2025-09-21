# 🚀 AIAlchemy - Quick GCP Deployment

## One-Click Deployment to Google Cloud Platform

### Prerequisites
1. **GCP Account** with billing enabled
2. **Google Cloud CLI** installed locally ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Docker** installed (for local testing)

### 🚀 Quick Deploy (5 minutes)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/archetana/AIAlchemy.git
   cd AIAlchemy
   ```

2. **Authenticate with GCP**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **Create GCP Project** (or use existing):
   ```bash
   gcloud projects create aialchemy-prod --name="AIAlchemy Production"
   gcloud config set project aialchemy-prod
   gcloud config set compute/region us-central1
   ```

4. **Run deployment script**:
   ```bash
   ./deploy-gcp.sh
   ```

### 🎯 What Gets Deployed

- **Backend API** → Cloud Run (FastAPI + SQLAlchemy)
- **Frontend Dashboard** → Cloud Run (React + Material-UI)
- **Database** → SQLite (included, upgradeable to Cloud SQL)
- **Static Assets** → Served via nginx

### 🌐 Access Your Application

After deployment completes, you'll get URLs like:
- **Frontend**: `https://aialchemy-frontend-xxx-uc.a.run.app`
- **Backend API**: `https://aialchemy-backend-xxx-uc.a.run.app`
- **API Docs**: `https://aialchemy-backend-xxx-uc.a.run.app/docs`

### 📊 Features Available

✅ **Dashboard Overview** with real-time metrics  
✅ **Pipeline Analytics** with interactive charts  
✅ **Application Management** with status tracking  
✅ **REST API** with comprehensive endpoints  
✅ **Material-UI Design** matching Figma mockups  
✅ **Responsive Layout** for mobile and desktop  

### 🔧 Management Commands

```bash
# View services
gcloud run services list

# View logs
gcloud logs tail 'resource.type=cloud_run_revision'

# Update backend
cd backend && gcloud run deploy aialchemy-backend --source .

# Update frontend  
cd frontend && gcloud run deploy aialchemy-frontend --source .

# Delete services
gcloud run services delete aialchemy-backend --region=us-central1
gcloud run services delete aialchemy-frontend --region=us-central1
```

### 💰 Estimated Costs

- **Development/Testing**: $0-5/month (free tier)
- **Light Production**: $10-30/month
- **High Traffic**: $50-200/month

Cloud Run charges only for requests, making it very cost-effective for variable traffic.

### 🔄 Upgrading to Production

For production use, consider:

1. **Database**: Upgrade to Cloud SQL PostgreSQL
2. **Domain**: Add custom domain with SSL
3. **Monitoring**: Enable Cloud Monitoring & Logging
4. **Security**: Configure Cloud IAM and secrets
5. **CDN**: Add Cloud CDN for global performance

See [GCP-DEPLOYMENT.md](./GCP-DEPLOYMENT.md) for detailed production setup.

### 🆘 Troubleshooting

**Build Fails**: Check Docker is running locally  
**Access Denied**: Run `gcloud auth login` again  
**API Errors**: Check backend logs with `gcloud logs tail`  
**Frontend Issues**: Verify REACT_APP_API_URL in logs  

### 📞 Support

- **Documentation**: [GCP-DEPLOYMENT.md](./GCP-DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/archetana/AIAlchemy/issues)
- **API Docs**: Available at `/docs` endpoint after deployment

---

**Ready to deploy?** Run `./deploy-gcp.sh` and you'll have AIAlchemy running on GCP in minutes! 🎉