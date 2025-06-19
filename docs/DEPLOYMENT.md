# Deployment Guide

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- Domain name (optional)
- SSL certificate (for production)

### Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd artbot-control-hub
```

2. **Create environment file:**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
ADMIN_PASSWORD=your-super-secure-admin-password-2025
MUSEUM_PASSWORD=museum-exhibition-password
JWT_SECRET=your-jwt-secret-key-for-token-signing
HUB_DOMAIN=https://your-domain.com
```

3. **Deploy with Docker Compose:**
```bash
docker-compose -f deployment/docker/docker-compose.yml up -d
```

4. **Verify deployment:**
```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Health check
curl http://localhost/api/system/health
```

### Custom Domain Setup

1. **Configure DNS:**
Point your domain to the server IP address.

2. **SSL Certificate (Let's Encrypt):**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

3. **Update nginx configuration:**
Edit `deployment/nginx/nginx.conf` to include SSL settings.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_PASSWORD` | Administrator password | Required |
| `MUSEUM_PASSWORD` | Museum staff password | Required |
| `JWT_SECRET` | JWT signing secret | Required |
| `HUB_DOMAIN` | Hub domain URL | http://localhost:8000 |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | info |

### Scaling and High Availability

#### Load Balancing
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
  
  nginx:
    deploy:
      replicas: 2
```

#### Database (Optional)
For persistent storage, add PostgreSQL:
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: artbot_hub
      POSTGRES_USER: artbot
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Monitoring

#### Health Checks
Built-in health check endpoints:
- `/api/system/health` - System health
- `/api/system/status` - Service status

#### Logging
Logs are stored in `./logs/` directory:
```bash
# View application logs
tail -f logs/app.log

# View nginx logs
docker-compose logs nginx
```

#### Prometheus (Optional)
Add monitoring with Prometheus:
```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
```

### Security

#### Firewall
```bash
# Only allow HTTP/HTTPS and SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### Password Security
- Use strong, unique passwords
- Rotate passwords regularly
- Consider using environment variable files with restricted permissions

#### Network Security
- Run behind reverse proxy (nginx)
- Use HTTPS in production
- Implement rate limiting
- Regular security updates

### Backup and Recovery

#### Backup Configuration
```bash
# Backup environment and configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env logs/

# Backup with docker volumes
docker run --rm -v artbot_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz /data
```

#### Recovery
```bash
# Restore configuration
tar -xzf backup-20240101.tar.gz

# Restart services
docker-compose down
docker-compose up -d
```

### Troubleshooting

#### Common Issues

1. **Cannot connect to backend:**
```bash
# Check backend health
docker-compose exec backend curl http://localhost:8000/

# Check logs
docker-compose logs backend
```

2. **WebSocket connection issues:**
```bash
# Check nginx configuration
docker-compose exec frontend nginx -t

# Verify WebSocket proxy
curl -H "Upgrade: websocket" -H "Connection: upgrade" http://localhost/ws/robots
```

3. **Agent registration fails:**
```bash
# Check network connectivity
ping hub-domain.com

# Verify API endpoint
curl -X POST http://hub-domain.com/api/agents/register -d '{"agent_id":"test"}'
```

#### Performance Tuning

1. **Nginx optimization:**
```nginx
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
```

2. **Backend optimization:**
```bash
# Increase worker processes
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

#### Log Analysis
```bash
# Find errors in logs
grep ERROR logs/app.log

# Monitor real-time logs
tail -f logs/app.log | grep -i error

# Check connection patterns
awk '/WebSocket/ {print $1, $4}' logs/app.log | sort | uniq -c
```

### Updates and Maintenance

#### Rolling Updates
```bash
# Update without downtime
docker-compose pull
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps frontend
```

#### Scheduled Maintenance
```bash
# Create maintenance script
#!/bin/bash
docker-compose down
docker system prune -f
docker-compose pull
docker-compose up -d
```

### Agent Deployment

See `AGENT_SETUP.md` for Pi agent installation instructions.

### Support

For issues and support:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test connectivity: Health check endpoints
4. Review documentation: API.md, ARCHITECTURE.md
