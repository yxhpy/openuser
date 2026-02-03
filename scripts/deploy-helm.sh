#!/bin/bash
# OpenUser Helm Deployment Script

set -e

echo "🚀 OpenUser Helm Deployment"
echo "==========================="

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

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

# Parse arguments
RELEASE_NAME=${1:-openuser}
NAMESPACE=${2:-openuser}
VALUES_FILE=${3:-helm/openuser/values.yaml}

echo "📝 Deploying OpenUser with Helm..."
echo "   Release name: $RELEASE_NAME"
echo "   Namespace: $NAMESPACE"
echo "   Values file: $VALUES_FILE"
echo ""

# Check if values file exists
if [ ! -f "$VALUES_FILE" ]; then
    echo "❌ Values file not found: $VALUES_FILE"
    exit 1
fi

echo "⚠️  WARNING: Please ensure you have updated the values file with secure passwords and keys!"
read -p "Have you updated the values file? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled. Please update values file first."
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade the Helm release
echo "🔨 Installing/Upgrading Helm release..."
helm upgrade --install $RELEASE_NAME helm/openuser \
    --namespace $NAMESPACE \
    --values $VALUES_FILE \
    --wait \
    --timeout 10m

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To check status:"
echo "  helm status $RELEASE_NAME -n $NAMESPACE"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/openuser-api -n $NAMESPACE"
echo ""
echo "To access the API:"
echo "  kubectl port-forward svc/openuser-api 8000:8000 -n $NAMESPACE"
echo "  Then visit: http://localhost:8000"
echo ""
echo "To uninstall:"
echo "  helm uninstall $RELEASE_NAME -n $NAMESPACE"
echo ""
