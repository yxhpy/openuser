# Kubernetes Deployment Guide

This guide explains how to deploy OpenUser on Kubernetes.

## Prerequisites

- Kubernetes cluster 1.24+ (minikube, GKE, EKS, AKS, or self-hosted)
- kubectl configured to access your cluster
- At least 8GB RAM and 4 CPU cores available
- 100GB storage for persistent volumes
- (Optional) Ingress controller installed (nginx-ingress recommended)
- (Optional) cert-manager for automatic SSL certificates

## Quick Start

1. **Update secrets**:
   ```bash
   # Edit k8s/secret.yaml and update all passwords and keys
   nano k8s/secret.yaml
   ```

2. **Deploy with script**:
   ```bash
   ./scripts/deploy-k8s.sh
   ```

## Manual Deployment

### 1. Update Configuration

Edit `k8s/secret.yaml` and update:
- `POSTGRES_PASSWORD` - Strong database password
- `JWT_SECRET_KEY` - Random secret key (use `openssl rand -hex 32`)
- Integration credentials (Feishu, WeChat Work) if needed

### 2. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 3. Apply Configurations

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
```

### 4. Deploy Database and Cache

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Wait for services to be ready
kubectl wait --for=condition=ready pod -l app=openuser-postgres -n openuser --timeout=300s
kubectl wait --for=condition=ready pod -l app=openuser-redis -n openuser --timeout=300s
```

### 5. Deploy Application

```bash
# Deploy API
kubectl apply -f k8s/api.yaml

# Deploy Celery workers
kubectl apply -f k8s/celery.yaml

# Wait for API to be ready
kubectl wait --for=condition=ready pod -l app=openuser-api -n openuser --timeout=300s
```

### 6. Deploy Ingress (Optional)

```bash
kubectl apply -f k8s/ingress.yaml
```

## Architecture

The Kubernetes deployment includes:

- **Namespace**: `openuser` - Isolated namespace for all resources
- **PostgreSQL**: StatefulSet with persistent storage
- **Redis**: StatefulSet with persistent storage
- **API**: Deployment with 3 replicas and horizontal pod autoscaling
- **Celery Worker**: Deployment with 2 replicas
- **Celery Beat**: Deployment with 1 replica
- **Ingress**: External access with SSL termination

## Accessing Services

### Port Forward (Development)

```bash
# API
kubectl port-forward svc/openuser-api 8000:8000 -n openuser

# PostgreSQL
kubectl port-forward svc/openuser-postgres 5432:5432 -n openuser

# Redis
kubectl port-forward svc/openuser-redis 6379:6379 -n openuser
```

### Ingress (Production)

Update `k8s/ingress.yaml` with your domain:

```yaml
hosts:
  - host: api.yourdomain.com
```

Then access via: https://api.yourdomain.com

## Management Commands

### View Pods

```bash
kubectl get pods -n openuser
```

### View Logs

```bash
# API logs
kubectl logs -f deployment/openuser-api -n openuser

# Worker logs
kubectl logs -f deployment/openuser-celery-worker -n openuser

# All logs
kubectl logs -f -l app=openuser-api -n openuser
```

### Execute Commands

```bash
# Run database migrations
kubectl exec -it deployment/openuser-api -n openuser -- alembic upgrade head

# Access shell
kubectl exec -it deployment/openuser-api -n openuser -- /bin/bash
```

### Scale Deployments

```bash
# Scale API
kubectl scale deployment openuser-api --replicas=5 -n openuser

# Scale workers
kubectl scale deployment openuser-celery-worker --replicas=4 -n openuser
```

### Update Deployment

```bash
# Update image
kubectl set image deployment/openuser-api api=openuser/api:v0.2.0 -n openuser

# Rollout status
kubectl rollout status deployment/openuser-api -n openuser

# Rollback
kubectl rollout undo deployment/openuser-api -n openuser
```

## Persistent Storage

### Storage Classes

Ensure your cluster has a default storage class:

```bash
kubectl get storageclass
```

### Persistent Volume Claims

The deployment creates these PVCs:

- `postgres-pvc`: 10Gi for PostgreSQL data
- `redis-pvc`: 5Gi for Redis data
- `models-pvc`: 20Gi for AI models (ReadWriteMany)
- `uploads-pvc`: 50Gi for user uploads (ReadWriteMany)

**Note**: `ReadWriteMany` access mode requires NFS or similar shared storage.

### Backup Volumes

```bash
# Backup PostgreSQL
kubectl exec -it deployment/openuser-postgres -n openuser -- \
  pg_dump -U openuser openuser > backup.sql

# Backup models (requires ReadWriteMany)
kubectl run backup --rm -it --image=busybox -n openuser -- \
  tar -czf /backup/models.tar.gz -C /app/models .
```

## Resource Management

### Resource Requests and Limits

Current configuration:

- **API**: 512Mi-2Gi RAM, 250m-1000m CPU
- **Worker**: 1Gi-4Gi RAM, 500m-2000m CPU
- **Beat**: 256Mi-512Mi RAM, 100m-250m CPU
- **PostgreSQL**: 256Mi-1Gi RAM, 100m-500m CPU
- **Redis**: 128Mi-512Mi RAM, 50m-250m CPU

Adjust in manifests based on workload.

### Horizontal Pod Autoscaling

Create HPA for API:

```bash
kubectl autoscale deployment openuser-api \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n openuser
```

## Monitoring

### Check Resource Usage

```bash
# Pod resource usage
kubectl top pods -n openuser

# Node resource usage
kubectl top nodes
```

### Events

```bash
kubectl get events -n openuser --sort-by='.lastTimestamp'
```

## Troubleshooting

### Pod Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n openuser

# Check events
kubectl get events -n openuser

# Check logs
kubectl logs <pod-name> -n openuser
```

### Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl get pod -l app=openuser-postgres -n openuser

# Test connection
kubectl exec -it deployment/openuser-api -n openuser -- \
  psql postgresql://openuser:password@openuser-postgres:5432/openuser
```

### Storage Issues

```bash
# Check PVCs
kubectl get pvc -n openuser

# Check PVs
kubectl get pv
```

### Ingress Not Working

```bash
# Check ingress
kubectl get ingress -n openuser
kubectl describe ingress openuser-ingress -n openuser

# Check ingress controller
kubectl get pods -n ingress-nginx
```

## Security Best Practices

1. **Use Secrets**: Never commit secrets to version control
2. **RBAC**: Configure role-based access control
3. **Network Policies**: Restrict pod-to-pod communication
4. **Pod Security**: Use security contexts and pod security policies
5. **Image Scanning**: Scan images for vulnerabilities
6. **TLS**: Enable TLS for all external communication
7. **Resource Limits**: Set resource limits to prevent resource exhaustion

## Production Checklist

- [ ] Update all secrets with strong passwords
- [ ] Configure persistent storage with backups
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure logging (ELK, Loki)
- [ ] Enable horizontal pod autoscaling
- [ ] Configure ingress with SSL certificates
- [ ] Set up network policies
- [ ] Configure RBAC
- [ ] Enable pod security policies
- [ ] Set up automated backups
- [ ] Configure alerting
- [ ] Document disaster recovery procedures

## Next Steps

- [Helm Deployment](HELM.md) - Simplified deployment with Helm
- [Monitoring Setup](MONITORING.md) - Set up monitoring and alerting
- [CI/CD Setup](CICD.md) - Automated deployment pipeline
