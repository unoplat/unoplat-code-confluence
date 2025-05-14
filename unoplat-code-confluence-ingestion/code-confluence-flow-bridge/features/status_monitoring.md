# Objective

To monitor status of temporal codebase workflows and capture error trace in an event of failure.

## Context

Possible Status of Jobs:
- SUBMITTED
- RUNNING
- FAILED
- TIMED_OUT
- COMPLETED

### Implementation details

In activity_inbound_interceptor.py we need to check if workflow is of type 