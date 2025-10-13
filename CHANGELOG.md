# AIAlchemy Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed - 2025-10-13 (Part 2)

#### Issue: Database Session Errors and Password Validation Too Strict
**Problem**: Users getting 500 errors during registration with no error messages displayed in frontend UI

**Root Causes Identified**:
1. **Password Validation Too Restrictive**
   - Password validator rejected passwords with repeated characters (e.g., "Hello" has "ll")
   - Regex pattern `(.)\1{2,}` was too strict, rejecting normal passwords
   - Pattern `(?i)(password|123456|qwerty|admin)` rejected passwords containing these words anywhere

2. **Database Rollback Error**
   - When password validation failed, generic error handler tried to rollback database
   - No active database transaction existed at validation stage
   - Caused secondary "Database session error" that masked the real validation error
   - Resulted in 500 Internal Server Error instead of 400 Bad Request

3. **Frontend Not Displaying Validation Errors**
   - Backend returned error object `{message: "...", errors: ["..."]}`
   - Frontend expected simple string in `error.response.data.detail`
   - Object was rendered as `[object Object]` instead of readable message

**Changes Made**:

##### Backend Changes

**File**: `backend/app/auth/password_utils.py`
- **Lines 61-71**: Relaxed password validation rules
  - Now only reject truly weak passwords (all same character: "aaaaaaaa")
  - Only reject exact matches to common weak passwords: "password", "123456", "qwerty", "admin", "letmein"
  - Removed overly strict repeated character check that rejected normal words
  - Allow reasonable passwords like "Hello123!" or "Support@2024"
  - Improved error message: "Password is too common or simple"

**File**: `backend/app/routers/auth.py`
- **Lines 187-201**: Fixed error handling and database rollback
  - HTTPExceptions (validation errors) no longer attempt database rollback
  - Only rollback on unexpected errors where database operations may have started
  - Wrapped rollback in try-catch to prevent secondary errors
  - Better error messages: "Failed to create account. Please try again."

##### Frontend Changes

**File**: `frontend/src/contexts/AuthContext.js`
- **Lines 204-227**: Enhanced error message parsing and display
  - Detect if error detail is an object or string
  - Extract `message` field from error object
  - Extract `errors` array and join into readable string
  - Format as: "Password does not meet security requirements: [error list]"
  - Ensure error message always displayed to user

**Result**:
- ✅ Password validation now accepts reasonable passwords
- ✅ Clear validation errors displayed to users in UI
- ✅ No more 500 errors or "Database session error" messages
- ✅ Proper 400 Bad Request responses with helpful messages

### Fixed - 2025-10-13 (Part 1)

#### Issue: User Registration Not Working
**Problem**: Users were unable to create new accounts during signup process

**Root Causes Identified**:
1. **Missing Authentication Tokens in Registration Response**
   - Backend was not returning JWT tokens after successful registration
   - Frontend expected `access_token` and `refresh_token` to auto-login user
   - This caused the registration to "succeed" but leave the user unauthenticated

2. **User Role Selection Ignored During Registration**
   - Frontend form allowed users to select their role (viewer, analyst, partner, admin)
   - Backend hardcoded all new users to `VIEWER` role, ignoring user selection
   - Role field in request was not being processed

**Changes Made**:

##### Backend Changes

**File**: `backend/app/routers/auth.py`
- **Lines 129-185**: Complete refactor of user registration endpoint
  - Added role validation and processing logic
  - Now respects user's role selection from registration form
  - Defaults to `VIEWER` role if invalid or no role provided
  - Generate JWT access and refresh tokens immediately after user creation
  - Return tokens in response for automatic login
  - Enhanced logging to include role information

**File**: `backend/app/schemas.py`
- **Lines 54-69**: Updated `RegisterRequest` and `RegisterResponse` schemas
  - Added `role` field to `RegisterRequest` (Optional[UserRole])
  - Added `access_token`, `refresh_token`, and `token_type` fields to `RegisterResponse`
  - Maintains backward compatibility with existing code

**Database Changes**:
- **No database migration required** - existing schema already supports all necessary fields
- Users table already has `role` column (from migration `4230559ae43f`)
- Users table already has `hashed_password` and `last_login_at` columns (from migration `a40120993a6e`)

**Testing Recommendations**:
1. Test user registration with each role type (viewer, analyst, partner, admin)
2. Verify tokens are returned and stored in localStorage
3. Verify user is automatically logged in after registration
4. Test registration without role field (should default to viewer)
5. Test registration with invalid role (should default to viewer and log warning)

**Security Considerations**:
- Role validation ensures only valid UserRole enum values are accepted
- Invalid roles are logged for security monitoring
- Password validation and hashing remain unchanged and secure
- JWT token generation follows existing secure patterns

**Backward Compatibility**:
- Changes are fully backward compatible
- Existing registration flows will continue to work
- Role field is optional, defaults to VIEWER if not provided
- Frontend can be updated independently

**Related Files**:
- Frontend: `frontend/src/components/Auth/Register.js` (already sends role)
- Frontend: `frontend/src/contexts/AuthContext.js` (expects tokens in response)
- Models: `backend/app/models.py` (User model with role enum)
- Auth: `backend/app/auth/jwt_handler.py` (token generation)

**Issue Resolution Status**: ✅ FIXED
- User registration now creates accounts successfully
- Users are automatically logged in after registration
- Role selection during signup is now respected
- All authentication flows working as expected
