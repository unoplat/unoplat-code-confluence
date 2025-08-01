# Loguru: Best Practices and Complete Guide

## Overview

Loguru is a library that aims to bring enjoyable logging in Python. It provides a simple, powerful interface that replaces Python's standard logging module with a more intuitive approach.

## Installation

```bash
pip install loguru
# or
uv add loguru
```

## Table of Contents

1. [Basic Configuration](#basic-configuration)
2. [Advanced Configuration](#advanced-configuration)
3. [Best Practices](#best-practices)
4. [Formatting & Filtering](#formatting--filtering)
5. [Production Patterns](#production-patterns)
6. [Common Recipes](#common-recipes)
7. [Troubleshooting](#troubleshooting)

## Basic Configuration

### Simple Setup

```python
from loguru import logger
import sys

# Basic usage - uses default stderr handler
logger.info("This is an informational message.")

# Remove default handler and add custom console handler
logger.remove()
logger.add(sys.stderr, format="{time} - {level} - {message}")
```

### File Logging with Levels

```python
from loguru import logger
import sys

# Remove default handler
logger.remove()

# Console handler with WARNING level
logger.add(sys.stderr, level="WARNING")

# File handler with INFO level
logger.add("app.log", level="INFO")

logger.debug("Debug message")  # Not logged (below INFO)
logger.info("Info message")    # Logged to file only
logger.warning("Warning")      # Logged to both console and file
logger.error("Error message")  # Logged to both console and file
```

### Multiple Handlers with Different Configurations

```python
from loguru import logger
import sys

logger.remove()

# Console handler with colors and specific format
logger.add(
    sys.stderr, 
    format="<green>{time}</green> | <level>{message}</level>",
    level="WARNING"
)

# File handler with detailed format
logger.add(
    "detailed.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG"
)

# JSON structured logging
logger.add("structured.log", serialize=True, level="INFO")
```

## Advanced Configuration

### File Rotation and Retention

```python
from loguru import logger

# Rotate file when it exceeds 500 MB
logger.add("app.log", rotation="500 MB")

# Rotate file daily at noon
logger.add("daily.log", rotation="12:00")

# Rotate file weekly
logger.add("weekly.log", rotation="1 week")

# Multiple rotation conditions (any condition triggers rotation)
logger.add("multi.log", rotation=["10 MB", "midnight"])

# Keep logs for maximum 10 days
logger.add("retained.log", retention="10 days")

# Compress rotated files
logger.add("compressed.log", rotation="1 day", compression="zip")

# Combined rotation, retention, and compression
logger.add(
    "production.log",
    rotation="100 MB",
    retention="30 days",
    compression="gz",
    level="INFO"
)
```

### Time-Based File Naming

```python
from loguru import logger

# Automatic time-based file naming
logger.add("logs/app_{time:YYYY-MM-DD_HH-mm-ss}.log")
logger.add("logs/daily_{time:YYYY-MM-DD}.log", rotation="1 day")
```

### Delayed File Creation

```python
from loguru import logger

# Create file only when first log message is written
logger.add("lazy.log", delay=True)
```

## Best Practices

### Thread-Safe Logging

```python
from loguru import logger
import threading

# Enable thread-safe logging with enqueue
logger.add("threaded.log", enqueue=True)

def worker(name):
    logger.info("Worker {} started", name)
    # Do work...
    logger.info("Worker {} finished", name)

# Create multiple threads
threads = [threading.Thread(target=worker, args=(f"Thread-{i}",)) for i in range(5)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

### Multiprocessing Support

#### Linux/Unix (Fork)

```python
import multiprocessing
from loguru import logger

def worker_process():
    logger.info("Executing function in child process")

if __name__ == "__main__":
    logger.add("multiprocess.log", enqueue=True)
    
    process = multiprocessing.Process(target=worker_process)
    process.start()
    process.join()
    
    logger.info("Main process done")
```

#### Windows (Spawn) - Method 1: Pass Logger

```python
import multiprocessing
from loguru import logger

def worker_process(logger_instance):
    logger_instance.info("Executing function in child process")

if __name__ == "__main__":
    logger.remove()  # Remove default handler (not picklable)
    logger.add("multiprocess.log", enqueue=True)
    
    process = multiprocessing.Process(target=worker_process, args=(logger,))
    process.start()
    process.join()
    
    logger.info("Main process done")
```

#### Windows (Spawn) - Method 2: Process Pool with Initializer

```python
from multiprocessing import Pool
from loguru import logger

# workers.py
class Worker:
    _logger = None
    
    @staticmethod
    def set_logger(logger_instance):
        Worker._logger = logger_instance
    
    def work(self, x):
        Worker._logger.info(f"Processing {x}")
        return x ** 2

# main.py
if __name__ == "__main__":
    logger.remove()
    logger.add("pool.log", enqueue=True)
    
    worker = Worker()
    with Pool(4, initializer=worker.set_logger, initargs=(logger,)) as pool:
        results = pool.map(worker.work, [1, 2, 3, 4, 5])
    
    logger.info("Pool processing complete: {}", results)
```

#### Multiprocessing with Context

```python
import multiprocessing
from loguru import logger

if __name__ == "__main__":
    context = multiprocessing.get_context("spawn")
    
    logger.remove()
    logger.add("context.log", enqueue=True, context=context)
    
    def worker():
        logger.info("Worker with context")
    
    with context.Pool(4) as pool:
        pool.map(worker, range(4))
```

### Exception Handling

```python
from loguru import logger

# Decorator for automatic exception logging
@logger.catch
def risky_function(x, y):
    return x / y

# Context manager for exception handling
def another_function():
    with logger.catch():
        # Risky code here
        result = 1 / 0

# Custom exception handling with reraise
@logger.catch(reraise=True)
def critical_function():
    # This will log the exception and re-raise it
    raise ValueError("Critical error")

# Exception handling with custom message
@logger.catch(message="Error in data processing")
def process_data():
    raise RuntimeError("Data corruption detected")

# Exclude specific exceptions
@logger.catch(exclude=KeyboardInterrupt)
def interruptible_task():
    # KeyboardInterrupt won't be caught
    while True:
        pass
```

### Performance Optimization

```python
from loguru import logger

# Lazy evaluation for expensive operations
def expensive_function():
    # Simulate expensive computation
    return sum(range(1000000))

# Only evaluated if DEBUG level is active
logger.opt(lazy=True).debug("Result: {}", lambda: expensive_function())

# Lazy evaluation with multiple parameters
logger.opt(lazy=True).debug(
    "Complex calculation: {} + {} = {}", 
    lambda: expensive_function(),
    lambda: another_expensive_function(),
    lambda: expensive_function() + another_expensive_function()
)
```

## Formatting & Filtering

### Custom Formatters

```python
from loguru import logger
import sys

# Dynamic padding formatter
class PaddingFormatter:
    def __init__(self):
        self.padding = 0
        self.fmt = "{time} | {level: <8} | {name}:{function}:{line}{extra[padding]} | {message}\n{exception}"
    
    def format(self, record):
        length = len("{name}:{function}:{line}".format(**record))
        self.padding = max(self.padding, length)
        record["extra"]["padding"] = " " * (self.padding - length)
        return self.fmt

formatter = PaddingFormatter()
logger.remove()
logger.add(sys.stderr, format=formatter.format)
```

### Call Stack Tracing Formatter

```python
import traceback
from itertools import takewhile
from loguru import logger
import sys

def tracing_formatter(record):
    # Filter out frames coming from Loguru internals
    frames = takewhile(lambda f: "/loguru/" not in f.filename, traceback.extract_stack())
    stack = " > ".join("{}:{}:{}".format(f.filename, f.name, f.lineno) for f in frames)
    record["extra"]["stack"] = stack
    return "{level} | {extra[stack]} - {message}\n{exception}"

logger.remove()
logger.add(sys.stderr, format=tracing_formatter)

def foo():
    logger.info("Deep call")

def bar():
    foo()

bar()
```

### Color Configuration

```python
from loguru import logger
import sys

# Custom color format
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Environment variable control
# Set NO_COLOR=1 to disable colors
# Set FORCE_COLOR=1 to force colors
# Set LOGURU_FORMAT="{time} | <lvl>{message}</lvl>" for custom default format
```

### Filtering

```python
from loguru import logger

# Filter by module name
logger.add("filtered.log", filter="my_module")

# Filter by level
logger.add("errors.log", filter=lambda record: record["level"].no >= 40)  # ERROR and CRITICAL

# Filter by custom criteria
logger.add(
    "api.log", 
    filter=lambda record: "api" in record.get("extra", {})
)

# Multiple filters
def complex_filter(record):
    return (
        record["level"].no >= 20 and  # INFO and above
        "database" not in record["message"].lower() and
        record.get("extra", {}).get("component") == "web"
    )

logger.add("complex.log", filter=complex_filter)

# Usage with filtering
logger.bind(component="web", user_id=123).info("User logged in")
logger.bind(component="database").info("Query executed")  # Filtered out
```

### Context Binding

```python
from loguru import logger

# Bind context data
user_logger = logger.bind(user_id=123, session="abc456")
user_logger.info("User action performed")

# Temporary contextualization
with logger.contextualize(task_id="task-789", worker="worker-1"):
    logger.info("Task started")
    # ... do work ...
    logger.info("Task completed")

# Filter based on bound context
logger.add("user_actions.log", filter=lambda record: "user_id" in record["extra"])
logger.add("tasks.log", filter=lambda record: "task_id" in record["extra"])
```

## Production Patterns

### Complete Application Configuration

```python
from loguru import logger
import sys
import os

def setup_logging():
    # Remove default handler
    logger.remove()
    
    # Console logging for development
    if os.getenv("ENVIRONMENT") == "development":
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG"
        )
    else:
        # Production console logging - minimal
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="WARNING"
        )
    
    # Application logs
    logger.add(
        "logs/app.log",
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        enqueue=True  # Thread-safe
    )
    
    # Error logs
    logger.add(
        "logs/errors.log",
        rotation="50 MB",
        retention="90 days",
        compression="gz",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
        enqueue=True
    )
    
    # Structured logs for monitoring
    logger.add(
        "logs/structured.log",
        rotation="200 MB",
        retention="7 days",
        serialize=True,
        level="INFO",
        enqueue=True
    )

# Call during application startup
setup_logging()
```

### Library vs Application Usage

```python
# For libraries - disable by default
from loguru import logger

# In your library's __init__.py
logger.disable("my_library")

# In your library code
def library_function():
    logger.info("Library operation")  # Won't be displayed by default

# In the application using your library
from my_library import library_function
from loguru import logger

# Enable library logging in the application
logger.enable("my_library")
logger.add("app.log")

library_function()  # Now this will be logged
```

### Structured Logging for Monitoring

```python
from loguru import logger
import json

# Custom serialization
def custom_serializer(record):
    subset = {
        "timestamp": record["time"].timestamp(),
        "level": record["level"].name,
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "extra": record.get("extra", {})
    }
    return json.dumps(subset)

def custom_sink(message):
    serialized = custom_serializer(message.record)
    # Send to monitoring system, e.g., ELK stack
    print(serialized)

logger.add(custom_sink)

# Usage with structured data
logger.bind(
    user_id=123,
    action="login",
    ip_address="192.168.1.1",
    response_time=0.245
).info("User authentication successful")
```

### Log Parsing and Analysis

```python
import dateutil.parser
from loguru import logger

# Parse existing log files
pattern = r"(?P<time>.*) \| (?P<level>[A-Z]+)\s* \| (?P<module>.*):(?P<function>.*):(?P<line>\d+) \| (?P<message>.*)"
cast_dict = {
    "time": dateutil.parser.parse,
    "line": int,
    "level": str.upper
}

for parsed_entry in logger.parse("logs/app.log", pattern, cast=cast_dict):
    print(f"Parsed: {parsed_entry}")
    # Process parsed log entries for analysis
```

## Common Recipes

### Network Logging (TCP)

#### Server (Log Collector)

```python
import socketserver
import pickle
import struct
import sys
from loguru import logger

class LoggingRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            
            record = pickle.loads(chunk)
            level, message = record["level"].name, record["message"]
            logger.patch(lambda r, record=record: r.update(record)).log(level, message)

if __name__ == "__main__":
    # Configure the logger with desired handlers
    logger.configure(handlers=[
        {"sink": "server.log", "rotation": "100 MB"},
        {"sink": sys.stderr}
    ])
    
    # Setup the server to receive log messages
    with socketserver.TCPServer(("localhost", 9999), LoggingRequestHandler) as server:
        server.serve_forever()
```

#### Client (Log Sender)

```python
import socket
import struct
import pickle
from loguru import logger

class SocketHandler:
    def __init__(self, host, port):
        self._host = host
        self._port = port
    
    def write(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        record = message.record
        data = pickle.dumps(record)
        slen = struct.pack(">L", len(data))
        sock.send(slen + data)
        sock.close()

if __name__ == "__main__":
    # Configure logger to send to server
    logger.configure(handlers=[{"sink": SocketHandler('localhost', 9999)}])
    
    # Use logger normally
    logger.info("Message from client")
    logger.error("Error from client")
```

### Integration with tqdm Progress Bars

```python
import time
from loguru import logger
from tqdm import tqdm

# Redirect logger output to tqdm.write to avoid breaking progress bar
logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

logger.info("Initializing process")

for i in tqdm(range(100), desc="Processing"):
    if i % 10 == 0:
        logger.info("Processed {} items", i)
    time.sleep(0.01)

logger.info("Process completed")
```

### Capturing stdout/stderr

```python
import contextlib
import sys
from loguru import logger

class StreamToLogger:
    def __init__(self, level="INFO"):
        self._level = level
    
    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())
    
    def flush(self):
        pass

# Setup
logger.remove()
logger.add("captured_output.log")
logger.add(sys.__stdout__)  # Also show on console

# Redirect stdout to logger
stream = StreamToLogger()
with contextlib.redirect_stdout(stream):
    print("This will be logged instead of printed to stdout")
    print("Multiple lines")
    print("All captured")

# You can also capture stderr
error_stream = StreamToLogger("ERROR")
with contextlib.redirect_stderr(error_stream):
    print("This is an error", file=sys.stderr)
```

### Migration from Standard Logging

```python
import logging
from loguru import logger

# Intercept standard logging and redirect to Loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from where original logging call was made
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Setup interception
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Configure Loguru
logger.remove()
logger.add("migrated.log", level="INFO")

# Now standard logging calls will be handled by Loguru
logging.info("This message comes from standard logging")
logger.info("This message comes from Loguru")
```

### Deep Copying for Independent Loggers

```python
import copy
from loguru import logger

def create_task_logger(task_id):
    # Create independent logger instance
    task_logger = copy.deepcopy(logger)
    task_logger.remove()  # Remove any inherited handlers
    task_logger.add(f"task_{task_id}.log", level="DEBUG")
    return task_logger

# Usage
logger_a = create_task_logger("A")
logger_b = create_task_logger("B")

logger_a.info("Task A message")  # Goes to task_A.log
logger_b.info("Task B message")  # Goes to task_B.log
```

### Async Support

```python
import asyncio
from loguru import logger

# Async sink function
async def async_sink(message):
    # Simulate async operation (e.g., sending to external service)
    await asyncio.sleep(0.1)
    print(f"Async: {message}", end="")

# Configure async logging
logger.add(async_sink, enqueue=True)

async def main():
    logger.info("Starting async operations")
    
    # Ensure all async messages are processed
    await logger.complete()
    
    logger.info("All operations completed")
    await logger.complete()

# Run async application
asyncio.run(main())
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Logs Not Appearing

```python
from loguru import logger
import sys

# Check current logger configuration
print(logger)  # Shows all handlers and their levels

# Common fix: Check if level is too restrictive
logger.remove()
logger.add(sys.stderr, level="DEBUG")  # Lower the level

# Common fix: Ensure handler is added
if not logger._core.handlers:
    logger.add(sys.stderr)
```

#### Issue: Colors Not Working

```python
from loguru import logger
import sys
import os

# Force color output
logger.remove()
logger.add(sys.stderr, colorize=True)

# Or use environment variable
os.environ["FORCE_COLOR"] = "1"
logger.add(sys.stderr)  # Will now use colors

# Check if terminal supports colors
print(f"Is TTY: {sys.stderr.isatty()}")
```

#### Issue: Multiprocessing Errors

```python
from loguru import logger
import multiprocessing

# Fix: Remove non-picklable handlers before multiprocessing
logger.remove()  # Remove default stderr handler
logger.add("multiprocess_safe.log", enqueue=True)

# For Windows, always pass logger explicitly or use context
if __name__ == "__main__":
    context = multiprocessing.get_context("spawn")
    # ... rest of multiprocessing code
```

#### Issue: Performance Problems

```python
from loguru import logger

# Use lazy evaluation for expensive operations
logger.opt(lazy=True).debug("Expensive: {}", lambda: expensive_computation())

# Use appropriate log levels in production
logger.remove()
logger.add("app.log", level="INFO")  # Skip DEBUG messages

# Use enqueue for high-throughput scenarios
logger.add("high_volume.log", enqueue=True)
```

#### Issue: Memory Usage with Large Files

```python
from loguru import logger

# Use rotation to prevent files from growing too large
logger.add(
    "app.log",
    rotation="100 MB",    # Rotate when file exceeds 100MB
    retention="10 days",  # Keep only 10 days worth of logs
    compression="gz"      # Compress old logs
)
```

#### Issue: Testing with Loguru

```python
import pytest
from loguru import logger

@pytest.fixture
def caplog_loguru(capfd):
    """Capture Loguru output for testing"""
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level="DEBUG")
    yield
    logger.remove()

def test_logging(caplog_loguru, capfd):
    logger.info("Test message")
    captured = capfd.readouterr()
    assert "Test message" in captured.out
```

### Debugging Logger Configuration

```python
from loguru import logger
import sys

def debug_logger_config():
    """Print current logger configuration for debugging"""
    print(f"Logger handlers: {len(logger._core.handlers)}")
    
    for handler_id, handler in logger._core.handlers.items():
        print(f"Handler {handler_id}:")
        print(f"  Sink: {handler._sink}")
        print(f"  Level: {handler._level_no} ({handler._level_name})")
        print(f"  Format: {handler._formatter}")
        print(f"  Filter: {handler._filter}")
        print(f"  Colorize: {handler._colorize}")
        print(f"  Serialize: {handler._serialize}")
        print(f"  Enqueue: {handler._enqueue}")
        print()

# Usage
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("debug.log", level="DEBUG", serialize=True)

debug_logger_config()
```

### Environment Variables Reference

```bash
# Disable colors globally
export NO_COLOR=1

# Force colors globally
export FORCE_COLOR=1

# Custom default format
export LOGURU_FORMAT="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

# Custom level colors
export LOGURU_DEBUG_COLOR="<blue>"
export LOGURU_INFO_COLOR="<green>"
export LOGURU_WARNING_COLOR="<yellow>"
export LOGURU_ERROR_COLOR="<red>"
export LOGURU_CRITICAL_COLOR="<bold red>"
```

## Summary

Loguru provides a powerful and intuitive logging interface that can handle everything from simple console output to complex production logging scenarios. Key takeaways:

1. **Always remove the default handler** when configuring custom logging
2. **Use `enqueue=True`** for thread-safe and multiprocessing scenarios
3. **Implement proper file rotation and retention** for production applications
4. **Use structured logging** with `serialize=True` or custom formatters for monitoring
5. **Handle exceptions** with `@logger.catch` decorator
6. **Use lazy evaluation** for performance-critical applications
7. **Configure different handlers** for different log levels and destinations
8. **Test your logging configuration** thoroughly in your target environment

This guide covers the official patterns and best practices for using Loguru effectively in production applications.