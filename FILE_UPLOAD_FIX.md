# File Upload Size Limit Fix - 100MB Support

## Problem
The application was returning `413 Request Entity Too Large` errors when uploading files, preventing users from uploading files larger than the default nginx limits (typically 1-8MB).

## Root Cause
Multiple layers had file size restrictions:
1. **Nginx Gateway** - Default `client_max_body_size` was too small
2. **Frontend Nginx** - Default upload limits
3. **Backend FastAPI** - Application-level file size validation
4. **File Storage Service** - Custom file size limits per category

## Solution Implemented

### 1. Backend File Size Limits ✅
- **File**: `backend/app/services/file_storage.py`
- **Change**: Updated `MAX_FILE_SIZES` to 100MB for all categories:
  ```python
  MAX_FILE_SIZES = {
      'document': 100 * 1024 * 1024,  # 100MB for documents
      'image': 100 * 1024 * 1024,     # 100MB for images 
      'video': 100 * 1024 * 1024,     # 100MB for videos
      'audio': 100 * 1024 * 1024,     # 100MB for audio
  }
  ```

### 2. Nginx Gateway Configuration ✅
- **File**: `nginx-gateway/nginx.conf`
- **Changes**:
  ```nginx
  http {
      # File upload size limits - Allow up to 100MB uploads
      client_max_body_size 100M;
      client_body_buffer_size 128k;
      client_body_timeout 300s;
      client_header_timeout 300s;
      
      # ... existing config ...
  }
  
  # API routes with extended timeouts
  location /api/ {
      # ... existing proxy settings ...
      
      # Proxy timeout settings for large file uploads
      proxy_connect_timeout 300s;
      proxy_send_timeout 300s;
      proxy_read_timeout 300s;
      send_timeout 300s;
  }
  ```

### 3. Frontend Nginx Configuration ✅
- **File**: `frontend/nginx.conf`
- **Changes**:
  ```nginx
  server {
      # File upload size limits - Allow up to 100MB uploads
      client_max_body_size 100M;
      client_body_buffer_size 128k;
      client_body_timeout 300s;
      client_header_timeout 300s;
      
      # ... existing config ...
  }
  ```

### 4. Centralized File Configuration ✅
- **New File**: `backend/app/core/file_config.py`
- **Purpose**: Centralized configuration for file upload settings
- **Features**:
  - Environment variable support for dynamic configuration
  - Helper methods for size formatting
  - Configurable timeout settings

### 5. New API Endpoint for Upload Configuration ✅
- **Endpoint**: `GET /api/uploads/config`
- **Purpose**: Allows clients to check current upload limits
- **Response**:
  ```json
  {
      "success": true,
      "max_file_sizes": {
          "document": "100.0MB",
          "image": "100.0MB", 
          "video": "100.0MB",
          "audio": "100.0MB"
      },
      "max_request_size_mb": "100.0MB",
      "upload_timeout_seconds": 300,
      "supported_file_types": ["application/pdf", "image/jpeg", ...],
      "storage_backend": "local"
  }
  ```

## Configuration Options

### Environment Variables (Optional)
You can customize file size limits using environment variables:

```bash
# Individual file type limits (bytes)
MAX_DOCUMENT_SIZE=104857600  # 100MB
MAX_IMAGE_SIZE=104857600     # 100MB  
MAX_VIDEO_SIZE=104857600     # 100MB
MAX_AUDIO_SIZE=104857600     # 100MB

# Maximum total request size
MAX_REQUEST_SIZE=104857600   # 100MB

# Upload timeout
UPLOAD_TIMEOUT_SECONDS=300   # 5 minutes
```

## Deployment Requirements

### For Local Development
1. Restart the backend service:
   ```bash
   cd backend && python -m uvicorn app.main:app --reload --port 8000
   ```

### For Production Deployment
1. **Container Rebuild Required** - The nginx configuration changes require rebuilding and redeploying containers:
   ```bash
   # For nginx gateway deployment
   ./deploy-nginx-gateway.sh
   
   # For full GCP deployment
   ./deploy-gcp.sh
   ```

2. **Verify Configuration**:
   ```bash
   # Check upload configuration
   curl https://your-app-url/api/uploads/config
   
   # Test file upload (replace with actual file)
   curl -X POST https://your-app-url/api/uploads/files \
        -F "file=@large-file.pdf" \
        -F "file_type=document"
   ```

## Testing

### Manual Testing Commands
```bash
# Test upload configuration endpoint
curl -X GET http://localhost:8000/api/uploads/config

# Test file upload with large file
curl -X POST http://localhost:8000/api/uploads/files \
     -F "file=@test-large-file.pdf" \
     -F "file_type=document" \
     -F "description=Test large file upload"
```

### Supported File Types
- **Documents**: PDF, DOC, DOCX, PPT, PPTX, TXT, CSV
- **Images**: JPG, JPEG, PNG, GIF  
- **Videos**: MP4, MOV, AVI
- **Audio**: MP3, WAV, M4A

## Troubleshooting

### Still Getting 413 Errors?
1. **Check nginx is reloaded**: Ensure containers are rebuilt after config changes
2. **Verify backend limits**: Check `/api/uploads/config` endpoint
3. **Client-side timeout**: Increase frontend request timeout for large files
4. **Network timeout**: Check cloud load balancer timeout settings if using GCP

### Performance Considerations
- Large file uploads (50MB+) may take 30-60 seconds over slow connections
- Consider implementing chunked uploads for files >100MB in future versions
- Monitor server memory usage with concurrent large uploads

## Future Enhancements
1. **Progress Indicators**: Implement upload progress tracking
2. **Chunked Uploads**: Support for files >100MB via chunked upload
3. **Async Processing**: Move file processing to background tasks
4. **CDN Integration**: Direct uploads to cloud storage with signed URLs