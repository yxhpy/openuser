# Performance and Load Testing

This directory contains performance benchmarks and load testing scenarios for the OpenUser API.

## Performance Benchmarks

Performance benchmarks use `pytest-benchmark` to measure the execution time of critical API endpoints.

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/performance/test_api_performance.py -m performance

# Run with benchmark comparison
pytest tests/performance/test_api_performance.py -m performance --benchmark-compare

# Save benchmark results
pytest tests/performance/test_api_performance.py -m performance --benchmark-save=baseline

# Compare against baseline
pytest tests/performance/test_api_performance.py -m performance --benchmark-compare=baseline
```

### Performance Metrics

The benchmarks measure:
- **Min**: Minimum execution time
- **Max**: Maximum execution time
- **Mean**: Average execution time
- **StdDev**: Standard deviation
- **Median**: Median execution time
- **IQR**: Interquartile range
- **Outliers**: Number of outlier measurements
- **Rounds**: Number of test rounds

### Performance Requirements

| Endpoint | Target (mean) | Acceptable (max) |
|----------|---------------|------------------|
| Health Check | < 10ms | < 50ms |
| Root Endpoint | < 20ms | < 100ms |
| Authentication | < 100ms | < 500ms |
| List Operations | < 200ms | < 1000ms |
| Create Operations | < 500ms | < 2000ms |

## Load Testing

Load testing uses `Locust` to simulate multiple concurrent users and measure system behavior under load.

### Running Load Tests

1. **Start the API server**:
   ```bash
   uvicorn src.api.main:app --reload
   ```

2. **Run Locust**:
   ```bash
   # Web UI mode (recommended)
   locust -f tests/performance/locustfile.py --host=http://localhost:8000

   # Headless mode
   locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
          --users 100 --spawn-rate 10 --run-time 5m --headless
   ```

3. **Access Web UI**:
   - Open http://localhost:8089
   - Set number of users and spawn rate
   - Start the test

### Load Testing Scenarios

#### OpenUserUser
Simulates a typical user performing various operations:
- Health checks (high frequency)
- Root endpoint access (medium frequency)
- User info retrieval (medium frequency)
- Agent listing (low frequency)
- Agent creation (low frequency)

#### AuthenticationUser
Focuses on authentication endpoints:
- User registration
- User login

#### ReadOnlyUser
Performs only read operations:
- Health checks
- User info retrieval
- Agent listing
- Task listing

### Load Testing Metrics

Monitor these metrics during load tests:
- **Requests per second (RPS)**: Total throughput
- **Response time**: 50th, 95th, 99th percentiles
- **Failure rate**: Percentage of failed requests
- **Concurrent users**: Number of simulated users
- **CPU usage**: Server CPU utilization
- **Memory usage**: Server memory utilization

### Load Testing Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| RPS | > 100 | > 50 |
| P95 Response Time | < 500ms | < 1000ms |
| P99 Response Time | < 1000ms | < 2000ms |
| Failure Rate | < 0.1% | < 1% |
| Concurrent Users | 100+ | 50+ |

## Continuous Performance Monitoring

### Pre-deployment Checklist

Before deploying to production:

1. ✅ Run performance benchmarks
2. ✅ Verify all endpoints meet performance requirements
3. ✅ Run load tests with expected peak load
4. ✅ Monitor resource usage (CPU, memory, database connections)
5. ✅ Check for memory leaks during extended load tests
6. ✅ Verify error rates under load
7. ✅ Test database query performance
8. ✅ Test cache hit rates

### Performance Regression Detection

```bash
# Save baseline before changes
pytest tests/performance/ -m performance --benchmark-save=before

# Make changes...

# Compare after changes
pytest tests/performance/ -m performance --benchmark-compare=before
```

If performance degrades by more than 20%, investigate before merging.

## Troubleshooting

### Slow Performance

If tests show slow performance:

1. **Check database queries**: Use query profiling
2. **Check cache hit rates**: Verify Redis is working
3. **Check external dependencies**: Network latency
4. **Check resource limits**: CPU, memory, connections
5. **Check for N+1 queries**: Use SQLAlchemy query logging

### High Failure Rates

If load tests show high failure rates:

1. **Check error logs**: Identify error patterns
2. **Check resource exhaustion**: Database connections, memory
3. **Check rate limiting**: May need to adjust limits
4. **Check timeouts**: May need to increase timeouts
5. **Check database locks**: Concurrent access issues

## Best Practices

1. **Run tests in isolation**: Don't run on production data
2. **Use realistic data**: Test with production-like data volumes
3. **Test peak scenarios**: Simulate expected peak load + 50%
4. **Monitor resources**: Track CPU, memory, database during tests
5. **Test gradually**: Ramp up load gradually to find breaking points
6. **Document results**: Keep records of performance test results
7. **Automate**: Integrate performance tests into CI/CD pipeline

## References

- [pytest-benchmark documentation](https://pytest-benchmark.readthedocs.io/)
- [Locust documentation](https://docs.locust.io/)
- [FastAPI performance tips](https://fastapi.tiangolo.com/deployment/concepts/)
