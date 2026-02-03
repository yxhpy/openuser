# Deployment Documentation

This directory contains comprehensive deployment guides for OpenUser.

## Quick Links

- [Docker Deployment](DOCKER.md) - Deploy with Docker and Docker Compose
- [Kubernetes Deployment](KUBERNETES.md) - Deploy on Kubernetes
- [Helm Deployment](HELM.md) - Deploy with Helm charts

## Deployment Options

### 1. Docker Compose (Recommended for Development)

**Best for**: Local development, testing, small deployments

**Pros**:
- Simple setup
- Easy to manage
- Good for single-server deployments
- Quick iteration

**Cons**:
- Limited scalability
- No built-in high availability
- Manual scaling

**Guide**: [Docker Deployment](DOCKER.md)

### 2. Kubernetes (Recommended for Production)

**Best for**: Production deployments, high availability, scalability

**Pros**:
- Horizontal scaling
- High availability
- Self-healing
- Rolling updates
- Resource management

**Cons**:
- Complex setup
- Requires Kubernetes knowledge
- Higher resource overhead

**Guide**: [Kubernetes Deployment](KUBERNETES.md)

### 3. Helm (Recommended for Production)

**Best for**: Production deployments with simplified management

**Pros**:
- All Kubernetes benefits
- Simplified deployment
- Easy configuration management
- Version control
- Rollback support

**Cons**:
- Requires Helm knowledge
- Additional abstraction layer

**Guide**: [Helm Deployment](HELM.md)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
│                    (Ingress/Service)                     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌───────▼────────┐
│   API Server   │       │   API Server   │
│   (Replica 1)  │       │   (Replica N)  │
└───────┬────────┘       └───────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌───────▼────────┐
│   PostgreSQL   │       │     Redis      │
│   (Database)   │       │    (Cache)     │
└────────────────┘       └────────────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌───────▼────────┐
│ Celery Worker  │       │  Celery Beat   │
│  (Background)  │       │  (Scheduler)   │
└────────────────┘       └────────────────┘
```

## Components

### Core Services

1. **API Server** (FastAPI)
   - REST API endpoints
   - WebSocket support
   - Authentication
   - File uploads

2. **PostgreSQL**
   - User data
   - Digital human configurations
   - Task metadata

3. **Redis**
   - Session cache
   - Task queue (Celery broker)
   - Result backend

4. **Celery Worker**
   - Background video generation
   - Scheduled tasks
   - Batch processing

5. **Celery Beat**
   - Task scheduling
   - Cron jobs

### Storage

1. **Models** (20GB+)
   - AI model files
   - Shared across pods (ReadWriteMany)

2. **Uploads** (50GB+)
   - User images
   - Audio files
   - Generated videos
   - Shared across pods (ReadWriteMany)

3. **Cache** (Ephemeral)
   - Temporary files
   - Processing cache

## Resource Requirements

### Minimum (Development)

- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB

### Recommended (Production)

- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 100GB+

### Per Component

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| API | 250m | 1000m | 512Mi | 2Gi |
| Worker | 500m | 2000m | 1Gi | 4Gi |
| Beat | 100m | 250m | 256Mi | 512Mi |
| PostgreSQL | 100m | 500m | 256Mi | 1Gi |
| Redis | 50m | 250m | 128Mi | 512Mi |

## Deployment Workflow

### 1. Preparation

```bash
# Clone repository
git clone https://github.com/yxhpy/openuser.git
cd openuser

# Update configuration
cp .env.docker .env
nano .env  # Update passwords and keys
```

### 2. Choose Deployment Method

#### Docker Compose

```bash
./scripts/deploy-docker.sh
```

#### Kubernetes

```bash
./scripts/deploy-k8s.sh
```

#### Helm

```bash
./scripts/deploy-helm.sh
```

### 3. Verify Deployment

```bash
# Check services
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### 4. Post-Deployment

- Run database migrations
- Create admin user
- Upload AI models
- Configure integrations
- Set up monitoring
- Configure backups

## Security Considerations

### Secrets Management

1. **Never commit secrets** to version control
2. **Use strong passwords** (20+ characters, random)
3. **Rotate secrets** regularly
4. **Use external secrets management** (Vault, AWS Secrets Manager)

### Network Security

1. **Enable TLS/SSL** for all external communication
2. **Use network policies** to restrict pod-to-pod communication
3. **Configure firewall rules** appropriately
4. **Use private networks** for internal services

### Access Control

1. **Enable RBAC** in Kubernetes
2. **Use service accounts** with minimal permissions
3. **Implement authentication** for all endpoints
4. **Enable audit logging**

## Monitoring and Observability

### Metrics

- API response times
- Request rates
- Error rates
- Resource usage (CPU, memory, disk)
- Queue lengths
- Task completion rates

### Logging

- Application logs
- Access logs
- Error logs
- Audit logs

### Alerting

- Service down
- High error rate
- Resource exhaustion
- Disk space low
- Database connection issues

## Backup Strategy

### What to Backup

1. **Database** - Daily full backup, hourly incremental
2. **User uploads** - Daily backup
3. **Configuration** - Version controlled
4. **Secrets** - Encrypted backup

### Backup Tools

- PostgreSQL: `pg_dump`, `pg_basebackup`
- Kubernetes: Velero
- Files: rsync, rclone

## Disaster Recovery

### Recovery Time Objective (RTO)

- Target: < 1 hour

### Recovery Point Objective (RPO)

- Target: < 1 hour (hourly backups)

### Recovery Procedures

1. Restore database from backup
2. Restore file storage
3. Redeploy application
4. Verify functionality
5. Update DNS if needed

## Scaling Guide

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale api=5

# Kubernetes
kubectl scale deployment openuser-api --replicas=5 -n openuser

# Helm
helm upgrade openuser helm/openuser --set api.replicaCount=5
```

### Vertical Scaling

Update resource limits in configuration files.

### Auto-scaling

Configure Horizontal Pod Autoscaler (HPA) in Kubernetes:

```bash
kubectl autoscale deployment openuser-api \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n openuser
```

## Troubleshooting

### Common Issues

1. **Service won't start** - Check logs and resource availability
2. **Database connection failed** - Verify credentials and network
3. **Out of memory** - Increase resource limits
4. **Disk full** - Clean up old files, increase storage
5. **Slow performance** - Scale horizontally, optimize queries

### Debug Commands

```bash
# Docker
docker-compose logs -f api
docker-compose ps

# Kubernetes
kubectl get pods -n openuser
kubectl logs -f deployment/openuser-api -n openuser
kubectl describe pod <pod-name> -n openuser

# Helm
helm status openuser -n openuser
helm get values openuser -n openuser
```

## Support

- **Documentation**: https://github.com/yxhpy/openuser/tree/main/docs
- **Issues**: https://github.com/yxhpy/openuser/issues
- **Discussions**: https://github.com/yxhpy/openuser/discussions

## Next Steps

- [Monitoring Setup](MONITORING.md) - Set up monitoring and alerting
- [CI/CD Setup](CICD.md) - Automated deployment pipeline
- [Performance Tuning](PERFORMANCE.md) - Optimize for production
