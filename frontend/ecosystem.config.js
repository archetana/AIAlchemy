module.exports = {
  apps: [
    {
      name: 'frontend-dev',
      script: 'npm',
      args: 'start',
      cwd: '/home/user/webapp/frontend',
      watch: false,
      env: {
        NODE_ENV: 'development',
        REACT_APP_API_BASE_URL: 'http://localhost:8000',
        PORT: 3000
      }
    }
  ]
};