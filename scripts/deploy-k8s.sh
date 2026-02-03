#!/bin/bash
# OpenUser Kubernetes Deployment Script

set -e

echo "🚀 OpenUser Kubernetes Deployment"
echo "=================================="

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

echo "📝 Deploying OpenUser to Kubernetes..."

# Apply namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply secrets (should be customized first)
echo "⚠️  WARNING: Please update k8s/secret.yaml with secure values before deploying!"
read -p "Have you updated the secrets? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled. Please update secrets first."
    exit 1
fi

# Apply configurations
echo "Applying configurations..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy PostgreSQL
echo "Deploying PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

# Deploy Redis
echo "Deploying Redis..."
kubectl apply -f k8s/redis.yaml

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=openuser-postgres -n openuser --timeout=300s

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=openuser-redis -n openuser --timeout=300s

# Deploy API
echo "Deploying API..."
kubectl apply -f k8s/api.yaml

# Deploy Celery workers
echo "Deploying Celery workers..."
kubectl apply -f k8s/celery.yaml

# Deploy Ingress
echo "Deploying Ingress..."
kubectl apply -f k8s/ingress.yaml

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
kubectl wait --for=condition=ready pod -l app=openuser-api -n openuser --timeout=300s

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To check status:"
echo "  kubectl get pods -n openuser"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/openuser-api -n openuser"
echo ""
echo "To access the API:"
echo "  kubectl port-forward svc/openuser-api 8000:8000 -n openuser"
echo "  Then visit: http://localhost:8000"
echo ""
