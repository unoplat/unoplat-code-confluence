# New file: implements safe Neo4j transaction helper using neomodel adb
from __future__ import annotations

import asyncio
import contextvars
from contextlib import asynccontextmanager

from neomodel import adb  # type: ignore

__all__ = ["managed_tx"]

# ---------------------------------------------------------------------------
# Internal state                                                                 
# ---------------------------------------------------------------------------
# True while the *current* asyncio Task is executing within a Neo4j transaction
_in_tx: contextvars.ContextVar[bool] = contextvars.ContextVar("_in_tx", default=False)

# NOTE: Neomodel maintains *one* AsyncDB session under the hood. Starting two
# transactions concurrently on that session triggers 'SystemError: Transaction
# in progress'. Therefore we serialize transactions with a global lock.

_tx_lock = asyncio.Lock()

@asynccontextmanager
async def managed_tx():
    """Async context manager for safe Neo4j transactions via neomodel.
    
    This function provides a transaction wrapper that prevents two critical issues:
    
    1. **Nested Transaction Prevention**: Guards against calling `adb.transaction` 
       within an already active transaction context in the same asyncio Task.
       Neo4j/neomodel raises `SystemError: Transaction in progress` when this occurs.
    
    2. **Concurrent Transaction Serialization**: Uses a global asyncio.Lock to 
       ensure only one transaction executes at a time across all Tasks. This is 
       necessary because neomodel maintains a single underlying AsyncDB session,
       and concurrent transactions on the same session trigger "Transaction in 
       progress" errors.
    
    Usage:
        ```python
        # Safe - single transaction
        async with managed_tx():
            await SomeNode.create({...})
        
        # Safe - prevents nesting within same Task
        async with managed_tx():
            await helper_function()  # Even if this also uses managed_tx()
        
        # Safe - serializes across concurrent Tasks  
        async def task_a():
            async with managed_tx():
                await NodeA.create({...})
        
        async def task_b():
            async with managed_tx():  # Waits for task_a to complete
                await NodeB.create({...})
        ```
    
    Architecture:
        - Uses `contextvars.ContextVar` to track transaction state per Task (checked FIRST)
        - Uses `asyncio.Lock` to serialize all transactions globally (acquired SECOND)
        - Delegates actual transaction management to `neomodel.adb.transaction`
    
    Raises:
        RuntimeError: If called within an already active transaction context
        
    Note:
        This creates a performance bottleneck by serializing all database 
        operations. However, it's necessary given neomodel's single-session 
        architecture. For high-throughput scenarios, consider batching 
        operations within fewer, larger transactions.
    """

    # Check for nested transaction FIRST to prevent deadlock
    # (asyncio.Lock is not reentrant, so same task acquiring twice would deadlock)
    if _in_tx.get():
        raise RuntimeError("Nested Neo4j transaction detected inside the same asyncio Task – this is not allowed.")

    # Serialize at most one transaction at a time to avoid 'Transaction in progress'
    async with _tx_lock:
        token = _in_tx.set(True)
        try:
            async with adb.transaction:
                yield
        finally:
            _in_tx.reset(token) 