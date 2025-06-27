# Docker Deployment Guide

This guide explains how to deploy the Job Search Flask application using Docker on your home server.

## Prerequisites

- Docker installed on your home server
- Docker Compose installed
- Basic knowledge of Docker commands

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd jobsearch

# Copy environment file and configure
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your actual values:

```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production

# API Keys
APOLLO_API_KEY=your-apollo-api-key
CLEARBIT_API_KEY=your-clearbit-api-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id
SERP_API_KEY=c1824007c8245f45a13212bad16a4d86581f35eb63b6842cb7eaee14e44bd8d2

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Build and Run

```bash
# Build and start the application
docker-compose up -d

# Check if the container is running
docker-compose ps

# View logs
docker-compose logs -f jobsearch-app
```

### 4. Access the Application

The application will be available at:
- **Local access**: http://localhost:5000
- **Network access**: http://YOUR_SERVER_IP:5000

## Management Commands

### Start/Stop the Application

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# Restart the application
docker-compose restart
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs jobsearch-app
```

### Update the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Management

```bash
# Access the container shell
docker-compose exec jobsearch-app bash

# Initialize database (if needed)
docker-compose exec jobsearch-app python init_db.py

# Create tables (if needed)
docker-compose exec jobsearch-app python create_tables.py
```

### Backup Database

```bash
# Create backup of SQLite database
docker-compose exec jobsearch-app cp /app/instance/jobsearch.db /app/instance/jobsearch_backup_$(date +%Y%m%d_%H%M%S).db

# Copy backup to host
docker cp jobsearch-flask-app:/app/instance/jobsearch_backup_*.db ./
```

## Troubleshooting

### Container Won't Start

1. Check logs:
   ```bash
   docker-compose logs jobsearch-app
   ```

2. Check if port 5000 is already in use:
   ```bash
   netstat -tulpn | grep :5000
   ```

3. If port is in use, change it in `docker-compose.yml`:
   ```yaml
   ports:
     - "5001:5000"  # Change 5001 to any available port
   ```

### Database Issues

1. Remove database volume and restart:
   ```bash
   docker-compose down
   docker volume rm jobsearch_jobsearch_data
   docker-compose up -d
   ```

### Permission Issues

1. Check container logs for permission errors
2. Ensure the application runs as non-root user (already configured)

### Health Check Failures

1. Check if the application is responding:
   ```bash
   curl http://localhost:5000/
   ```

2. Increase health check timeout in `docker-compose.yml` if needed

## Security Considerations

1. **Change the SECRET_KEY**: Use a strong, unique secret key in production
2. **Firewall**: Configure your firewall to only allow necessary ports
3. **Reverse Proxy**: Consider using nginx or traefik as a reverse proxy
4. **SSL/TLS**: Set up HTTPS for production use
5. **Environment Variables**: Never commit `.env` file to version control

## Performance Tuning

### Adjust Worker Processes

Edit the `CMD` in `Dockerfile` to change the number of workers:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:create_app()"]
```

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  jobsearch-app:
    # ... other configuration
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## Monitoring

### Container Stats

```bash
# View resource usage
docker stats jobsearch-flask-app

# View container information
docker inspect jobsearch-flask-app
```

### Application Health

The application includes a health check endpoint. You can monitor it with:

```bash
curl http://localhost:5000/
```

## Support

If you encounter issues:

1. Check the logs first: `docker-compose logs -f`
2. Verify environment variables are set correctly
3. Ensure all required API keys are valid
4. Check network connectivity and firewall settings
