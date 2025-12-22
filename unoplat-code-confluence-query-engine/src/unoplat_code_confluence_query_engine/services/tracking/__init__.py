"""Tracking services for agent lifecycle and progress management.

This package contains services for:
- Agent lifecycle event persistence (snapshots to PostgreSQL)
- Per-codebase progress tracking
- ElectricSQL event delta persistence

All services in this package handle write operations for tracking agent execution state.
"""
