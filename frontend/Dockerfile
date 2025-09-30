# Optimized React frontend for production deployment
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies - production optimized
RUN npm ci --only=production --silent

# Copy source code
COPY . .

# Build for production with optimizations
ENV NODE_ENV=production
ENV REACT_APP_ENVIRONMENT=production
ENV GENERATE_SOURCEMAP=false
RUN npm run build

# Production stage with nginx
FROM nginx:alpine as production

# Install curl for health checks
RUN apk --no-cache add curl

# Copy built app
COPY --from=builder /app/build /usr/share/nginx/html

# Simple nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Health check for frontend
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]