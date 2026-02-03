#!/bin/bash
# Run performance tests without coverage requirements

echo "Running performance benchmark tests..."
pytest tests/performance/test_api_performance.py -m performance --no-cov -v

echo ""
echo "Performance tests completed!"
echo ""
echo "To run load tests:"
echo "1. Start the API server: uvicorn src.api.main:app --reload"
echo "2. Run locust: locust -f tests/performance/locustfile.py --host=http://localhost:8000"
echo "3. Open http://localhost:8089 in your browser"
