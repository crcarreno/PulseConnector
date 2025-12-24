# Feature: Heavy Query Protection & Predictable Performance
## Overview

PulseConnector implements a high-performance data gateway designed to handle high levels of concurrency in lightweight queries, maintaining stability and predictability even when heavy queries are present.

The system does not attempt to run heavy workloads uncontrollably, but rather protects the overall user experience by limiting the impact of such queries on other users.

## Objective
- Light queries maintain low latency even under high concurrency.
- Heavy queries do not degrade the entire system.
- The backend never crashes, but rather degrades in a controlled manner.
- Performance is predictable and measurable, not dependent on ORM magic.

## Query Type Definitions
### Light Query

- Small table (≤ 10 records)
- Execution time: milliseconds
- Typical use: frequent reads, high concurrency
- System impact: minimal

### Heavy Query
- Large table (~1000 records)
- Large payload
- Variable execution time
- High impact on:
  - workers
  - connection pool
  - p95 latency

## System Behavior Under Load
- Light queries scale linearly to the concurrency limit.
- Heavy queries define p95, not p50.
- When multiple heavy queries coincide:
  - The system does not crash.
  - The system does not lose connections.
  - The system does not enter deadlock.
  - The system temporarily degrades throughput.
  - This behavior is intentional and documented.

## Functional limits

<div align="center">

| Appearance         | Behavior                     |
|--------------------|------------------------------|
| Light Concurrency  | High (100+ users)            |
| Heavy Concurrency  | Limited by design            |
| p50                | Stable and low               |
| p95                | Dominated by heavy queries   |
| Failures           | Minimal, associated with timeouts |
| Stability          | Guaranteed                   |
| Post-Load Recovery | Immediate                    |

</div>


## Key Design Decision

PulseConnector prioritizes stability and predictability over absolute throughput in mixed-load scenarios.

This makes it ideal as:
- API Data Gateway
- ODATA Layer
- Integration Middleware
- Controlled Reporting Backend

## Consolidated Load Test Table

Common environment across all tests:

- Hardware:
  - CPU: Intel Core i5 – 11th generation (1 effective core)
  - RAM: 8 GB
- OS: Linux
- Architecture:
  - Native SQL (no ORM)
  - Explicit connection pool
  - Waitress as a WSGI server
- Load:
  - Mix of light and heavy queries
  - Heavy ≈ 1000 records

| Test | Concurrent Users | Infrastructure          | Approximate RPS | p50      | p95            | Stability | Conclusion                 |
|------| --------------------- |-------------------------|-----------------| -------- | -------------- | ----------- | -------------------------- |
| Test 1 | 1                     | ORM + engine            | Low             | Low     | High           | Medium       | Limiting architecture     |
| Test 2 | 10                    | ORM + engine            | Low             | Low     | Very High       | Medium       | Structural bottleneck         |
| Test 3 | 50                    | ORM + engine            | Flat            | Low     | Very High       | Low        | Not scalable               |
| Test 4 | 50                    | SQL native + pool       | 15–17           | Low     | Moderate       | High        | Significant structural improvement    |
| Test 5 | 50                    | Pool + waitress ajustado | 15–16           | Low     | Isolated spikes | High        | Healthy infrastructure       |
| Test 6 | 100                   | App + Locust            | 3–11            | Low     | High           | High        | External CPU contention     |
| Test 7 | 200                   | App + Locust            | 2–10            | Variable | Very High       | Very High    | Functional limit reached |


## Test 3
![Test 3](images/screenshots/test/chart_test_1.png)

## Test 4
![Test 4](images/screenshots/test/chart_test_2.png)

## Test 5
![Test 5](images/screenshots/test/chart_test_3.png)

## Test 6
![Test 6](images/screenshots/test/chart_test_4.png)

## Test 7
![Test 7](images/screenshots/test/chart_test_5.png)


## Correct interpretation of the table

The architecture ceases to be the problem after Test 4.

From 100 users onwards, the observed limit is not in the backend, but in the test environment.

- At 200 users:
  - The system does not crash.
  - The limit is in the concurrency of heavy queries.

- The tool demonstrates:
  - stability
  - recovery
  - absence of leaks
  - predictable behavior

## Conclusion

PulseConnector can sustain high concurrency on modest hardware (8 GB RAM, 11th Gen i5), maintaining stability and control under mixed workloads.
The operational limit is not technical, but functional, and is explicitly defined by the impact of heavy queries.
This makes PulseConnector a system that is:

- reliable
- measurable
- true about its limits
- suitable for real-world production