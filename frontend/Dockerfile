# Multi-stage Dockerfile for React frontend
# Optimized for production deployment on Google Cloud Run with nginx

# Stage 1: Build stage - using Node 16 LTS for better compatibility
FROM node:16-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies step by step for better debugging
RUN echo "=== Checking versions ==="
RUN npm --version
RUN node --version
RUN echo "=== Installing npm dependencies ==="
RUN npm install --legacy-peer-deps --force
RUN echo "=== Fixing ajv dependency conflict ==="
RUN npm install ajv@^8.12.0 --save --legacy-peer-deps
RUN echo "=== Cleaning npm cache ==="
RUN npm cache clean --force
RUN echo "=== Dependencies installation completed ==="

# Copy source code
COPY . .

# Build application for production
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV REACT_APP_VERSION=$REACT_APP_VERSION

RUN echo "=== Building React application ==="
RUN npm run build
RUN echo "=== Build completed successfully ==="

# Stage 2: Production stage with nginx
FROM nginx:alpine as production

# Install curl for health checks
RUN apk --no-cache add curl

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy startup script and nginx config
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chmod +x /docker-entrypoint.sh


# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start application
ENTRYPOINT ["/docker-entrypoint.sh"]