# Helm Deployment Guide

This guide explains how to deploy OpenUser using Helm charts.

## Prerequisites

- Kubernetes cluster 1.24+
- Helm 3.0+ installed
- kubectl configured to access your cluster
- At least 8GB RAM and 4 CPU cores available
- 100GB storage for persistent volumes

## Quick Start

1. **Update values**:
   ```bash
   # Edit helm/openuser/values.yaml
   nano helm/openuser/values.yaml
   ```

2. **Deploy with script**:
   ```bash
   ./scripts/deploy-helm.sh
   ```

## Manual Deployment

### 1. Update Configuration

Edit `helm/openuser/values.yaml` and update:

```yaml
secrets:
  jwtSecretKey: "your-secure-random-key"
  postgresPassword: "your-secure-password"
  # Add integration credentials if needed
  feishuAppSecret: ""
  wechatCorpSecret: ""
```

### 2. Install Chart

```bash
helm install openuser helm/openuser \
  --namespace openuser \
  --create-namespace \
  --wait
```

### 3. Verify Installation

```bash
# Check release status
helm status openuser -n openuser

# Check pods
kubectl get pods -n openuser

# Check services
kubectl get svc -n openuser
```

## Configuration

### Common Configurations

#### Scaling

```yaml
# values.yaml
api:
  replicaCount: 5

celeryWorker:
  replicaCount: 4
```

#### Resources

```yaml
# values.yaml
api:
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "4Gi"
      cpu: "2000m"
```

#### Ingress

```yaml
# values.yaml
ingress:
  enabled: true
  hosts:
    - host: api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: openuser-tls
      hosts:
        - api.yourdomain.com
```

#### Storage

```yaml
# values.yaml
persistence:
  models:
    enabled: true
    size: 50Gi
  uploads:
    enabled: true
    size: 100Gi
```

### Override Values

#### Using --set

```bash
helm install openuser helm/openuser \
  --set api.replicaCount=5 \
  --set secrets.jwtSecretKey="your-key" \
  --namespace openuser
```

#### Using Custom Values File

```bash
# Create custom-values.yaml
cat > custom-values.yaml <<EOF
api:
  replicaCount: 5
secrets:
  jwtSecretKey: "your-secure-key"
  postgresPassword: "your-secure-password"
EOF

# Install with custom values
helm install openuser helm/openuser \
  --values custom-values.yaml \
  --namespace openuser
```

## Management Commands

### Upgrade Release

```bash
# Upgrade with new values
helm upgrade openuser helm/openuser \
  --namespace openuser \
  --values custom-values.yaml \
  --wait

# Upgrade with new image
helm upgrade openuser helm/openuser \
  --set image.tag=v0.2.0 \
  --namespace openuser
```

### Rollback Release

```bash
# List revisions
helm history openuser -n openuser

# Rollback to previous revision
helm rollback openuser -n openuser

# Rollback to specific revision
helm rollback openuser 2 -n openuser
```

### Uninstall Release

```bash
# Uninstall (keeps PVCs)
helm uninstall openuser -n openuser

# Uninstall and delete PVCs
helm uninstall openuser -n openuser
kubectl delete pvc --all -n openuser
```

### View Values

```bash
# View all values
helm get values openuser -n openuser

# View all values including defaults
helm get values openuser -n openuser --all
```

## Advanced Configuration

### External Database

Use external PostgreSQL instead of bundled:

```yaml
# values.yaml
postgresql:
  enabled: false

api:
  env:
    DATABASE_URL: "postgresql://user:pass@external-host:5432/openuser"
```

### External Redis

Use external Redis instead of bundled:

```yaml
# values.yaml
redis:
  enabled: false

api:
  env:
    REDIS_URL: "redis://external-host:6379/0"
    CELERY_BROKER_URL: "redis://external-host:6379/1"
    CELERY_RESULT_BACKEND: "redis://external-host:6379/2"
```

### GPU Support

Enable GPU for AI models:

```yaml
# values.yaml
api:
  env:
    DEVICE: cuda
  resources:
    limits:
      nvidia.com/gpu: 1

celeryWorker:
  env:
    DEVICE: cuda
  resources:
    limits:
      nvidia.com/gpu: 1
```

### Multiple Environments

Create environment-specific values:

```bash
# values-dev.yaml
api:
  replicaCount: 1
  env:
    OPENUSER_ENV: development
    OPENUSER_DEBUG: "true"

# values-prod.yaml
api:
  replicaCount: 5
  env:
    OPENUSER_ENV: production
    OPENUSER_DEBUG: "false"

# Deploy to dev
helm install openuser-dev helm/openuser \
  --values values-dev.yaml \
  --namespace openuser-dev

# Deploy to prod
helm install openuser-prod helm/openuser \
  --values values-prod.yaml \
  --namespace openuser-prod
```

## Monitoring and Observability

### Prometheus Integration

```yaml
# values.yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

### Grafana Dashboards

Import OpenUser dashboards:

```bash
# Add Grafana dashboard ConfigMap
kubectl apply -f monitoring/grafana-dashboard.yaml
```

## Backup and Restore

### Backup

```bash
# Backup Helm values
helm get values openuser -n openuser > backup-values.yaml

# Backup database
kubectl exec -it deployment/openuser-postgres -n openuser -- \
  pg_dump -U openuser openuser > backup.sql

# Backup PVCs
kubectl get pvc -n openuser -o yaml > backup-pvcs.yaml
```

### Restore

```bash
# Restore from backup
helm install openuser helm/openuser \
  --values backup-values.yaml \
  --namespace openuser

# Restore database
cat backup.sql | kubectl exec -i deployment/openuser-postgres -n openuser -- \
  psql -U openuser openuser
```

## Troubleshooting

### Chart Installation Failed

```bash
# Check Helm release status
helm status openuser -n openuser

# View installation logs
helm get notes openuser -n openuser

# Debug template rendering
helm template openuser helm/openuser --debug
```

### Values Not Applied

```bash
# Verify values
helm get values openuser -n openuser --all

# Check pod environment
kubectl exec -it deployment/openuser-api -n openuser -- env
```

### Upgrade Failed

```bash
# Check upgrade status
helm status openuser -n openuser

# Rollback if needed
helm rollback openuser -n openuser

# Force upgrade
helm upgrade openuser helm/openuser \
  --force \
  --namespace openuser
```

## Best Practices

1. **Version Control**: Store custom values files in version control
2. **Secrets Management**: Use external secrets management (Vault, Sealed Secrets)
3. **Testing**: Test chart changes in dev environment first
4. **Documentation**: Document custom configurations
5. **Monitoring**: Enable monitoring and alerting
6. **Backups**: Regular backups of values and data
7. **Updates**: Keep Helm chart and dependencies updated
8. **Security**: Regular security audits and updates

## Production Checklist

- [ ] Update all secrets with strong passwords
- [ ] Configure persistent storage with backups
- [ ] Set appropriate resource limits
- [ ] Enable monitoring and alerting
- [ ] Configure ingress with SSL
- [ ] Set up external database (optional)
- [ ] Configure autoscaling
- [ ] Document custom configurations
- [ ] Test disaster recovery procedures
- [ ] Set up CI/CD pipeline

## Next Steps

- [Monitoring Setup](MONITORING.md) - Set up monitoring and alerting
- [CI/CD Setup](CICD.md) - Automated deployment pipeline
- [Scaling Guide](SCALING.md) - Horizontal and vertical scaling
