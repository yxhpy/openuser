# Monitoring and Observability Guide

This guide explains the monitoring and observability infrastructure for OpenUser.

## Overview

OpenUser uses a comprehensive monitoring stack:

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Alertmanager**: Alert routing and notification
- **Exporters**: Metrics exporters for various services

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│   Prometheus   │   │     Loki       │   │  Alertmanager  │
│   (Metrics)    │   │    (Logs)      │   │   (Alerts)     │
└───────┬────────┘   └───────┬────────┘   └───────┬────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                     ┌────────▼────────┐
                     │     Grafana     │
                     │ (Visualization) │
                     └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│  API Metrics   │   │  System Logs   │   │  Slack/Email   │
│   (FastAPI)    │   │   (Promtail)   │   │ (Notifications)│
└────────────────┘   └────────────────┘   └────────────────┘
```

## Quick Start

### Docker Compose

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access services
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Alertmanager: http://localhost:9093
```

### Kubernetes

```bash
# Deploy monitoring stack
kubectl apply -f k8s/monitoring/

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# Open http://localhost:3000
```

## Components

### 1. Prometheus

**Purpose**: Metrics collection and time-series database

**Configuration**: `monitoring/prometheus/prometheus.yml`

**Metrics Collected**:
- API request rates and latencies
- Error rates
- CPU and memory usage
- Database connections
- Cache hit rates
- Custom application metrics

**Scrape Targets**:
- OpenUser API (port 8000)
- PostgreSQL Exporter (port 9187)
- Redis Exporter (port 9121)
- Node Exporter (port 9100)
- Kubernetes metrics

**Access**: http://localhost:9090

### 2. Grafana

**Purpose**: Visualization and dashboarding

**Configuration**: `monitoring/grafana/`

**Default Credentials**:
- Username: `admin`
- Password: `admin` (change on first login)

**Pre-configured Dashboards**:
- API Overview
- System Metrics
- Database Performance
- Cache Performance
- Application Logs

**Access**: http://localhost:3000

### 3. Loki

**Purpose**: Log aggregation and querying

**Configuration**: `monitoring/loki/loki-config.yml`

**Log Sources**:
- Application logs (JSON format)
- System logs
- Docker container logs
- Kubernetes pod logs

**Retention**: 31 days

**Access**: http://localhost:3100

### 4. Alertmanager

**Purpose**: Alert routing and notification

**Configuration**: `monitoring/prometheus/alertmanager.yml`

**Alert Channels**:
- Slack
- Email
- PagerDuty
- Webhook

**Access**: http://localhost:9093

### 5. Exporters

#### Node Exporter
- **Purpose**: System metrics (CPU, memory, disk, network)
- **Port**: 9100

#### PostgreSQL Exporter
- **Purpose**: Database metrics
- **Port**: 9187
- **Metrics**: Connections, queries, replication lag

#### Redis Exporter
- **Purpose**: Cache metrics
- **Port**: 9121
- **Metrics**: Memory usage, hit rate, evictions

## Metrics

### API Metrics

```python
# Example: Instrumenting FastAPI with Prometheus
from prometheus_client import Counter, Histogram, Gauge

# Request counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Response time histogram
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Active connections gauge
active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)
```

### Custom Metrics

Add custom metrics to your application:

```python
from prometheus_client import Counter, Gauge, Histogram

# Video generation metrics
video_generation_total = Counter(
    'video_generation_total',
    'Total video generations',
    ['mode', 'status']
)

video_generation_duration = Histogram(
    'video_generation_duration_seconds',
    'Video generation duration',
    ['mode']
)

# Queue metrics
celery_queue_length = Gauge(
    'celery_queue_length',
    'Celery queue length',
    ['queue']
)
```

## Alerts

### Alert Severity Levels

- **Critical**: Immediate action required (paging)
- **Warning**: Attention needed (Slack/email)
- **Info**: Informational (logged)

### Pre-configured Alerts

#### API Alerts
- **APIDown**: API is unreachable
- **HighErrorRate**: Error rate > 5%
- **HighResponseTime**: P95 latency > 1s
- **HighCPUUsage**: CPU usage > 80%
- **HighMemoryUsage**: Memory usage > 1.5GB

#### Infrastructure Alerts
- **NodeDown**: Node is unreachable
- **HighNodeCPU**: Node CPU > 80%
- **HighNodeMemory**: Node memory > 85%
- **DiskSpaceLow**: Disk usage > 85%
- **DiskSpaceCritical**: Disk usage > 95%

#### Database Alerts
- **PostgreSQLDown**: Database is unreachable
- **PostgreSQLTooManyConnections**: > 80 connections
- **PostgreSQLSlowQueries**: Queries > 60s
- **RedisDown**: Cache is unreachable
- **RedisHighMemory**: Memory usage > 90%

### Alert Configuration

Edit alert rules in `monitoring/prometheus/alerts/`:

```yaml
groups:
  - name: custom_alerts
    interval: 30s
    rules:
      - alert: CustomAlert
        expr: custom_metric > threshold
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Custom alert triggered"
          description: "Metric value is {{ $value }}"
```

### Alert Routing

Configure alert routing in `monitoring/prometheus/alertmanager.yml`:

```yaml
route:
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'
```

## Dashboards

### Creating Dashboards

1. **Access Grafana**: http://localhost:3000
2. **Login**: admin/admin
3. **Create Dashboard**: Click "+" → "Dashboard"
4. **Add Panel**: Click "Add panel"
5. **Configure Query**: Select Prometheus datasource
6. **Save Dashboard**: Click "Save" icon

### Example Queries

#### API Request Rate
```promql
rate(http_requests_total[5m])
```

#### Error Rate
```promql
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

#### P95 Latency
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### CPU Usage
```promql
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

#### Memory Usage
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

### Importing Dashboards

Import community dashboards:

1. Go to Dashboards → Import
2. Enter dashboard ID or upload JSON
3. Select Prometheus datasource
4. Click Import

**Recommended Dashboards**:
- Node Exporter Full: 1860
- PostgreSQL Database: 9628
- Redis Dashboard: 11835
- FastAPI Observability: 16110

## Logging

### Log Format

Use structured JSON logging:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Querying Logs

Use LogQL in Grafana:

```logql
# All logs from API
{job="openuser-api"}

# Error logs only
{job="openuser-api"} |= "ERROR"

# Logs with specific field
{job="openuser-api"} | json | level="error"

# Rate of errors
rate({job="openuser-api"} |= "ERROR" [5m])
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Request Rate**: Requests per second
2. **Error Rate**: Percentage of failed requests
3. **Latency**: Response time (P50, P95, P99)
4. **Saturation**: Resource utilization (CPU, memory, disk)

### SLIs and SLOs

Define Service Level Indicators (SLIs) and Objectives (SLOs):

```yaml
# Example SLOs
availability_slo: 99.9%  # 43 minutes downtime/month
latency_slo: 95% < 500ms  # 95% of requests under 500ms
error_rate_slo: < 1%  # Less than 1% error rate
```

### Monitoring SLOs

Create alerts for SLO violations:

```yaml
- alert: SLOViolation
  expr: |
    (
      sum(rate(http_requests_total{status=~"2.."}[30d]))
      /
      sum(rate(http_requests_total[30d]))
    ) < 0.999
  labels:
    severity: critical
  annotations:
    summary: "Availability SLO violated"
```

## Troubleshooting

### Prometheus Not Scraping

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check service discovery
curl http://localhost:9090/api/v1/targets/metadata

# Verify metrics endpoint
curl http://localhost:8000/metrics
```

### Grafana Not Showing Data

1. Check datasource connection
2. Verify Prometheus is running
3. Check query syntax
4. Verify time range

### Alerts Not Firing

```bash
# Check alert rules
curl http://localhost:9090/api/v1/rules

# Check Alertmanager
curl http://localhost:9093/api/v1/alerts

# Verify alert configuration
promtool check rules monitoring/prometheus/alerts/*.yml
```

### High Cardinality Issues

Avoid high cardinality labels:

```python
# Bad: User ID as label (high cardinality)
requests_total.labels(user_id=user_id).inc()

# Good: Use aggregated metrics
requests_total.labels(endpoint=endpoint).inc()
```

## Best Practices

1. **Use Structured Logging**: JSON format for easy parsing
2. **Add Context**: Include request IDs, user IDs in logs
3. **Monitor SLOs**: Define and track service level objectives
4. **Set Up Alerts**: Alert on symptoms, not causes
5. **Dashboard Organization**: Group related metrics
6. **Regular Review**: Review and update alerts/dashboards
7. **Retention Policy**: Balance storage vs. retention needs
8. **Security**: Secure Grafana with authentication
9. **Backup**: Backup Grafana dashboards and Prometheus data
10. **Documentation**: Document custom metrics and alerts

## Security

### Grafana Security

```yaml
# grafana.ini
[security]
admin_user = admin
admin_password = secure_password
secret_key = random_secret_key

[auth]
disable_login_form = false
disable_signout_menu = false

[auth.anonymous]
enabled = false
```

### Prometheus Security

```yaml
# prometheus.yml
global:
  external_labels:
    cluster: 'production'

# Enable basic auth
basic_auth_users:
  admin: $2y$10$...  # bcrypt hash
```

### Network Security

- Use TLS for all connections
- Restrict access with firewall rules
- Use VPN for remote access
- Enable authentication on all services

## Maintenance

### Regular Tasks

- **Daily**: Review critical alerts
- **Weekly**: Check dashboard accuracy
- **Monthly**: Review and update SLOs
- **Quarterly**: Audit alert rules
- **Annually**: Review retention policies

### Backup

```bash
# Backup Grafana dashboards
curl -H "Authorization: Bearer $API_KEY" \
  http://localhost:3000/api/search?type=dash-db | \
  jq -r '.[] | .uid' | \
  xargs -I {} curl -H "Authorization: Bearer $API_KEY" \
  http://localhost:3000/api/dashboards/uid/{} > dashboard_{}.json

# Backup Prometheus data
tar -czf prometheus-backup.tar.gz /prometheus/data
```

### Cleanup

```bash
# Clean old Prometheus data
curl -X POST http://localhost:9090/api/v1/admin/tsdb/clean_tombstones

# Clean old Loki logs (automatic with retention policy)
```

## Support

- **Documentation**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/
- **Loki Docs**: https://grafana.com/docs/loki/
- **Issues**: https://github.com/yxhpy/openuser/issues
