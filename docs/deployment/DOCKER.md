# Docker Deployment Guide

This guide explains how to deploy OpenUser using Docker and Docker Compose.

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- At least 4GB RAM available
- 20GB disk space for models and data

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yxhpy/openuser.git
   cd openuser
   ```

2. **Configure environment**:
   ```bash
   cp .env.docker .env
   # Edit .env and update configuration values
   nano .env
   ```

3. **Deploy with script**:
   ```bash
   ./scripts/deploy-docker.sh
   ```

## Manual Deployment

### 1. Create Environment File

Copy the template and update values:

```bash
cp .env.docker .env
```

**Important**: Update these values in `.env`:
- `POSTGRES_PASSWORD` - Strong database password
- `JWT_SECRET_KEY` - Random secret key (use `openssl rand -hex 32`)
- Integration credentials (Feishu, WeChat Work) if needed

### 2. Create Required Directories

```bash
mkdir -p data models cache uploads
```

### 3. Build Images

```bash
docker-compose build
```

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

## Service Architecture

The Docker Compose setup includes:

- **postgres**: PostgreSQL 15 database
- **redis**: Redis 7 cache and message broker
- **api**: FastAPI application (3 replicas for load balancing)
- **celery-worker**: Background task workers
- **celery-beat**: Scheduled task scheduler

## Accessing Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery-worker
```

### Check Status

```bash
docker-compose ps
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart api
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes

```bash
docker-compose down -v
```

## Data Persistence

Data is persisted in Docker volumes:

- `postgres_data`: Database data
- `redis_data`: Redis data

Local directories are mounted:

- `./data`: Application data
- `./models`: AI models
- `./cache`: Cache files
- `./uploads`: User uploads

## Scaling

Scale API or worker replicas:

```bash
# Scale API to 5 replicas
docker-compose up -d --scale api=5

# Scale workers to 4 replicas
docker-compose up -d --scale celery-worker=4
```

## Backup and Restore

### Backup Database

```bash
docker-compose exec postgres pg_dump -U openuser openuser > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose exec -T postgres psql -U openuser openuser
```

### Backup Volumes

```bash
# Backup models
tar -czf models-backup.tar.gz models/

# Backup uploads
tar -czf uploads-backup.tar.gz uploads/
```

## Troubleshooting

### Service Won't Start

Check logs:
```bash
docker-compose logs api
```

### Database Connection Issues

Ensure PostgreSQL is healthy:
```bash
docker-compose ps postgres
docker-compose exec postgres pg_isready -U openuser
```

### Out of Memory

Increase Docker memory limit in Docker Desktop settings or adjust resource limits in `docker-compose.yml`.

### Permission Issues

Fix ownership:
```bash
sudo chown -R 1000:1000 data models cache uploads
```

## Production Considerations

1. **Use strong passwords**: Generate secure passwords for all services
2. **Enable HTTPS**: Use a reverse proxy (nginx, Traefik) with SSL certificates
3. **Resource limits**: Adjust memory and CPU limits based on workload
4. **Monitoring**: Add monitoring tools (Prometheus, Grafana)
5. **Backups**: Set up automated backup schedules
6. **Logging**: Configure centralized logging (ELK stack)
7. **Security**: Use Docker secrets for sensitive data
8. **Updates**: Regularly update images and dependencies

## Next Steps

- [Kubernetes Deployment](KUBERNETES.md)
- [Helm Deployment](HELM.md)
- [Monitoring Setup](MONITORING.md)
