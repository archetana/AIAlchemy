# File Upload System Documentation

## Overview

The AIAlchemy file upload system provides secure, scalable file storage for startup applications including pitch decks, financial documents, team information, and media files.

## Architecture

### Backend Components

```
File Upload Flow:
Client → FastAPI Upload Endpoint → File Storage Service → Database → Storage Backend
                                      ↓
                               Security Validation
                                      ↓
                               Local Storage / Google Cloud Storage
```

### Storage Backends

#### Local Storage (Development)
- **Path**: `./uploads/{startup_id}/{file_type}/{filename}`
- **Use**: Development and testing
- **Configuration**: `USE_GOOGLE_CLOUD_STORAGE=false`

#### Google Cloud Storage (Production)
- **Bucket**: Configurable via `GOOGLE_CLOUD_STORAGE_BUCKET`
- **Path**: `gs://bucket/{startup_id}/{file_type}/{filename}`
- **Use**: Production deployment
- **Configuration**: `USE_GOOGLE_CLOUD_STORAGE=true`

## API Endpoints

### Upload Files
```http
POST /api/uploads/startup/{startup_id}/files
Content-Type: multipart/form-data

Parameters:
- files: List[UploadFile] (required)
- file_type: str (optional, default: "document")
- description: str (optional)
```

**Example Response:**
```json
{
  "success": true,
  "uploaded_files": [
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "pitch_deck.pdf",
      "size": 2048576,
      "type": "application/pdf",
      "status": "uploaded"
    }
  ],
  "errors": [],
  "summary": {
    "total_files": 1,
    "successful_uploads": 1,
    "failed_uploads": 0
  }
}
```

### List Files
```http
GET /api/uploads/startup/{startup_id}/files?file_type=pitch_deck&limit=50
```

**Example Response:**
```json
{
  "success": true,
  "startup_id": 1,
  "files": [
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440000",
      "original_filename": "pitch_deck.pdf",
      "file_type": "pitch_deck",
      "content_type": "application/pdf",
      "file_size": 2048576,
      "description": "Series A pitch deck",
      "upload_timestamp": "2025-01-20T10:30:00Z",
      "is_processed": false,
      "download_url": "/api/uploads/files/550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "total_files": 1,
  "file_types": ["pitch_deck"]
}
```

### Download File
```http
GET /api/uploads/files/{file_id}
```

**Response**: File content with appropriate headers for download.

### Delete File
```http
DELETE /api/uploads/files/{file_id}
```

### Upload Statistics
```http
GET /api/uploads/stats/summary?startup_id={startup_id}
```

## Supported File Types

### Documents
- **PDF**: `.pdf` (application/pdf)
- **Word**: `.doc`, `.docx` (application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document)
- **PowerPoint**: `.ppt`, `.pptx` (application/vnd.ms-powerpoint, application/vnd.openxmlformats-officedocument.presentationml.presentation)

### Images
- **JPEG**: `.jpg`, `.jpeg` (image/jpeg)
- **PNG**: `.png` (image/png)
- **GIF**: `.gif` (image/gif)

### Videos
- **MP4**: `.mp4` (video/mp4)
- **QuickTime**: `.mov` (video/quicktime)
- **AVI**: `.avi` (video/x-msvideo)

### Audio
- **MP3**: `.mp3` (audio/mpeg)
- **WAV**: `.wav` (audio/wav)
- **M4A**: `.m4a` (audio/mp4)

## File Size Limits

| Category | Maximum Size |
|----------|--------------|
| Documents | 50 MB |
| Images | 10 MB |
| Videos | 500 MB |
| Audio | 100 MB |

## File Organization

### File Types
- `pitch_deck` - Investor presentation materials
- `financial_docs` - Financial models, statements
- `team_info` - Team resumes, bios
- `legal_docs` - Legal documents, contracts
- `media` - Videos, images, audio files
- `other` - Miscellaneous documents

### Storage Structure
```
uploads/
├── {startup_id}/
│   ├── pitch_deck/
│   │   └── {uuid}.pdf
│   ├── financial_docs/
│   │   └── {uuid}.xlsx
│   ├── team_info/
│   │   └── {uuid}.pdf
│   └── media/
│       └── {uuid}.mp4
```

## Security Features

### File Validation
- **MIME type checking** - Validates file type based on content
- **Extension validation** - Ensures extension matches content type
- **Size validation** - Enforces size limits by file category
- **Content scanning** - Basic security validation (extensible to virus scanning)

### Access Control
- **Authentication required** - All endpoints require valid authentication
- **Startup ownership** - Users can only access files for authorized startups
- **File isolation** - Files are organized by startup ID

### Data Protection
- **File hashing** - SHA-256 hash for deduplication and integrity
- **Metadata encryption** - Sensitive metadata stored securely
- **Audit logging** - All file operations are logged

## Configuration

### Environment Variables

```bash
# File Storage Configuration
USE_GOOGLE_CLOUD_STORAGE=false          # true for GCS, false for local
LOCAL_UPLOAD_PATH=./uploads             # Local storage directory
GOOGLE_CLOUD_STORAGE_BUCKET=aialchemy-uploads  # GCS bucket name
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json  # GCS credentials

# File Processing
MAX_UPLOAD_SIZE=500MB                   # Global maximum file size
ALLOWED_EXTENSIONS=pdf,doc,docx,ppt,pptx,jpg,png,mp4,mov,mp3,wav
```

### Google Cloud Storage Setup

**Required Commands** (run these manually):

```bash
# 1. Enable APIs
gcloud services enable storage.googleapis.com

# 2. Create bucket
gsutil mb -p PROJECT_ID -c STANDARD -l us-central1 gs://aialchemy-uploads

# 3. Set CORS policy
gsutil cors set cors.json gs://aialchemy-uploads

# 4. Create service account
gcloud iam service-accounts create aialchemy-storage \
    --display-name="AIAlchemy Storage Service Account"

# 5. Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# 6. Generate key
gcloud iam service-accounts keys create ./gcs-service-account.json \
    --iam-account=aialchemy-storage@PROJECT_ID.iam.gserviceaccount.com
```

## Database Schema

### UploadedFile Model
```sql
CREATE TABLE uploaded_files (
    id VARCHAR(36) PRIMARY KEY,                    -- UUID
    startup_application_id INTEGER NOT NULL,      -- Foreign key
    original_filename VARCHAR(500) NOT NULL,      -- User's filename
    stored_filename VARCHAR(500) NOT NULL,        -- Generated filename
    file_type VARCHAR(100),                       -- Category
    content_type VARCHAR(200) NOT NULL,           -- MIME type
    file_size INTEGER NOT NULL,                   -- Size in bytes
    file_hash VARCHAR(64),                        -- SHA-256 hash
    file_path VARCHAR(1000) NOT NULL,             -- Storage path
    relative_path VARCHAR(500),                   -- Relative path
    storage_backend VARCHAR(50) DEFAULT 'local',  -- Backend type
    is_processed BOOLEAN DEFAULT FALSE,           -- Processing status
    processing_progress INTEGER DEFAULT 0,        -- Progress %
    description TEXT,                             -- User description
    metadata_json JSON,                           -- Additional metadata
    is_safe BOOLEAN DEFAULT TRUE,                 -- Security scan result
    upload_timestamp TIMESTAMP DEFAULT NOW(),     -- Upload time
    processed_at TIMESTAMP,                       -- Processing completion
    last_accessed_at TIMESTAMP,                   -- Last access
    FOREIGN KEY (startup_application_id) REFERENCES startup_applications(id)
);
```

## Testing

### Manual Testing
```bash
# Test file upload service
cd backend
python test_file_upload.py
```

### API Testing with curl
```bash
# Upload file
curl -X POST "http://localhost:8000/api/uploads/startup/1/files" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@pitch_deck.pdf" \
  -F "file_type=pitch_deck" \
  -F "description=Series A pitch presentation"

# List files
curl "http://localhost:8000/api/uploads/startup/1/files"

# Download file
curl "http://localhost:8000/api/uploads/files/{file_id}" -o downloaded_file.pdf
```

## Integration with Frontend

### Upload Component Usage
```javascript
import { uploadsApi } from '../services/api';

// Upload files
const uploadFiles = async (startupId, files, fileType) => {
  try {
    const response = await uploadsApi.uploadFiles(startupId, fileType, files);
    return response.data;
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};

// List files
const getFiles = async (startupId, fileType) => {
  try {
    const response = await uploadsApi.getStartupFiles(startupId, fileType);
    return response.data.files;
  } catch (error) {
    console.error('Failed to fetch files:', error);
    throw error;
  }
};
```

## Monitoring and Maintenance

### Key Metrics
- **Upload success rate** - Percentage of successful uploads
- **Storage usage** - Total storage consumed
- **Processing time** - Time from upload to processed
- **Error rates** - Upload and processing failures

### Maintenance Tasks
- **Storage cleanup** - Remove deleted files from storage
- **Orphaned files** - Clean up files without database records
- **Storage optimization** - Compress or archive old files
- **Security scans** - Regular virus/malware scanning

## Troubleshooting

### Common Issues

#### Upload Failures
- **File too large** - Check size limits in configuration
- **Invalid file type** - Verify MIME type and extension
- **Storage full** - Check available disk space or GCS quotas
- **Permissions** - Verify service account permissions for GCS

#### Performance Issues
- **Slow uploads** - Check network bandwidth and server resources
- **High memory usage** - Implement streaming uploads for large files
- **Database locks** - Optimize database queries and indexes

#### Storage Issues
- **GCS access denied** - Verify service account key and permissions
- **Local storage permissions** - Check file system permissions
- **File not found** - Verify file paths and storage backend configuration

---

**Next Steps**: Implement frontend upload components and integrate with existing startup application flow.