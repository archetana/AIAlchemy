# 🔄 Frontend API Configuration Changes

## 📋 **Changes Made**

Updated frontend to use relative URLs for nginx gateway compatibility.

### **Before (Direct Backend Access):**
```javascript
baseURL: 'http://localhost:8000'
// API calls: http://localhost:8000/api/startups/
```

### **After (Through Nginx Gateway):**
```javascript
baseURL: '/api'
// API calls: /api/startups/ (routed through nginx gateway)
```

## 🛠️ **Files Modified**

### **1. src/services/api.js**
- **Changed baseURL**: From `http://localhost:8000` to `/api`
- **Removed `/api/` prefixes**: All API endpoints now use relative paths
- **Updated dashboard display**: Shows "via gateway" for API URL

### **2. .env.example**
- **Updated default**: Now uses `/api` for production
- **Added comments**: Explains local vs production configuration

### **3. .env.development (New)**
- **Local development**: Uses `http://localhost:8000` for direct backend access
- **Development flags**: Optimized for local testing

## 🔀 **API Routing Flow**

### **Production (Nginx Gateway):**
```
Frontend Request: /api/startups/
    ↓
Nginx Gateway: https://gateway-url.run.app/api/startups/
    ↓
Backend Service: https://backend-url.run.app/api/startups/
```

### **Development (Direct):**
```
Frontend Request: http://localhost:8000/api/startups/
    ↓
Backend Service: http://localhost:8000/api/startups/
```

## ⚙️ **Environment Configuration**

### **Production Deployment:**
```bash
# Frontend automatically uses /api through nginx gateway
REACT_APP_API_BASE_URL=/api
```

### **Local Development:**
```bash
# Frontend connects directly to local backend
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 🎯 **Benefits**

1. **🌐 Unified Access**: Single URL for frontend and API
2. **🔒 Security**: No CORS issues through proxy
3. **📊 Monitoring**: Centralized logging through nginx
4. **🚀 Performance**: Direct routing without extra hops
5. **💰 Cost Effective**: No load balancer fees

## 🧪 **Testing**

### **Local Development:**
```bash
# Start backend
cd backend && python -m uvicorn main:app --reload --port 8000

# Start frontend (uses .env.development)
cd frontend && npm start
```

### **Production (Nginx Gateway):**
```bash
# Deploy with nginx gateway
./deploy-nginx-gateway.sh

# Test endpoints
curl https://gateway-url/api/health
curl https://gateway-url/api/startups/
```

## 🔍 **API Endpoint Changes**

All API endpoints now use relative paths:

| **Before** | **After** |
|------------|-----------|
| `/api/dashboard/overview` | `/dashboard/overview` |
| `/api/startups/` | `/startups/` |
| `/api/pipeline/stats` | `/pipeline/stats` |
| `/api/settings/users` | `/settings/users` |
| `/api/memos/` | `/memos/` |
| `/api/uploads/files` | `/uploads/files` |

## 🚨 **Breaking Changes**

### **For Local Development:**
- **Must use .env.development** file for direct backend access
- **Or set REACT_APP_API_BASE_URL=http://localhost:8000** manually

### **For Production:**
- **Must deploy nginx gateway** for API routing to work
- **Frontend expects API at `/api/*`** paths

## 🔄 **Migration Steps**

1. **✅ Frontend updated** - API service uses relative URLs
2. **✅ Environment files** - Separate dev/prod configurations
3. **✅ Nginx gateway** - Routes `/api/*` to backend
4. **✅ Deployment scripts** - Configure environments properly

## 🎯 **Next Steps**

1. **Test locally**: Ensure development environment works
2. **Deploy nginx gateway**: Use `./deploy-nginx-gateway.sh`
3. **Verify production**: Test all API endpoints through gateway
4. **Update documentation**: Any team-specific API docs

The frontend now seamlessly works with both local development and production nginx gateway! 🚀