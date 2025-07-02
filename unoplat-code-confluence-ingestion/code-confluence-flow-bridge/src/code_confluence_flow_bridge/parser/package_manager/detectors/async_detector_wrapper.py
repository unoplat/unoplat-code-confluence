"""
Async wrapper for PythonCodebaseDetector with SSE progress tracking support.

This module provides an async interface to the PythonCodebaseDetector that runs
in a ThreadPoolExecutor and communicates progress updates via asyncio.Queue.

Based on Python 3.12 asyncio best practices from asyncio-practices.md:
- Uses loop.run_in_executor() for blocking operations
- Avoids threading.Timer (double-threading anti-pattern)
- Implements proper async/await patterns for heartbeats
- Uses asyncio.run_coroutine_threadsafe() for thread-safe communication
- Follows structured concurrency with proper cleanup
"""

from src.code_confluence_flow_bridge.models.configuration.settings import CodebaseConfig
from src.code_confluence_flow_bridge.parser.package_manager.detectors.codebase_auto_detector import (
    PythonCodebaseDetector,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.progress_models import (
    DetectionProgress,
    DetectionResult,
    DetectionState,
)

import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
import functools
import time
from typing import Callable, List, Optional


class AsyncDetectorWrapper:
    """
    Async wrapper for PythonCodebaseDetector with progress tracking.
    
    Runs the detector in a ThreadPoolExecutor and provides real-time progress
    updates via asyncio.Queue for SSE streaming. Follows Python 3.12 asyncio 
    best practices to avoid common anti-patterns.
    """
    
    def __init__(self, executor: ThreadPoolExecutor, is_local: bool = False):
        """
        Initialize the async wrapper.
        
        Args:
            executor: ThreadPoolExecutor to run blocking detector operations
            is_local: Whether to detect local repositories
        """
        self.executor = executor
        self.is_local = is_local
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._start_time: Optional[float] = None
    
    async def detect_codebases_async(
        self,
        git_url: str,
        github_token: Optional[str] = None,
        progress_queue: Optional[asyncio.Queue] = None
    ) -> DetectionResult:
        """
        Detect codebases asynchronously with progress tracking.
        
        Uses asyncio.run_in_executor() to run blocking detection in ThreadPoolExecutor
        while maintaining thread-safe communication for progress updates.
        
        Args:
            git_url: GitHub repository URL
            github_token: Optional GitHub token for authentication
            progress_queue: Optional queue for progress updates (maxsize=100)
            
        Returns:
            DetectionResult with codebases and timing information
            
        Raises:
            Exception: If detection fails
        """
        self._start_time = time.time()
        
        # Send initial progress
        if progress_queue:
            await self._send_progress(
                progress_queue,
                DetectionState.INITIALIZING,
                "Starting codebase detection...",
                git_url
            )
        
        try:
            # Create detector instance with github_token and rules path
            rules_path = None  # Uses default rules.yaml
            detector = PythonCodebaseDetector(
                rules_path=rules_path,
                github_token=github_token
            )
            
            # Get current event loop for thread-safe callbacks
            loop = asyncio.get_running_loop()
            
            # Create progress callback for thread-safe communication
            progress_callback = None
            if progress_queue:
                progress_callback = self._create_thread_safe_progress_callback(
                    loop, progress_queue, git_url
                )
            
            # Start heartbeat task (async pattern, not threading.Timer)
            if progress_queue:
                self._heartbeat_task = asyncio.create_task(
                    self._heartbeat_loop(progress_queue, git_url)
                )
            
            # Run blocking detection in thread pool
            codebases = await loop.run_in_executor(
                self.executor,
                functools.partial(
                    self._run_detector_with_progress,
                    detector,
                    git_url,
                    progress_callback
                )
            )
            
            # Calculate duration
            duration = time.time() - self._start_time if self._start_time else 0.0
            
            # Send completion progress
            if progress_queue:
                await self._send_progress(
                    progress_queue,
                    DetectionState.COMPLETE,
                    f"Detection completed. Found {len(codebases)} codebases.",
                    git_url
                )
            
            # Return CodebaseConfig objects directly (Pydantic handles serialization)
            return DetectionResult(
                repository_url=git_url,
                duration_seconds=duration,
                codebases=codebases,
                error=None
            )
            
        except Exception as e:
            # Calculate duration even on error
            duration = time.time() - self._start_time if self._start_time else 0.0
            
            # Send error progress
            if progress_queue:
                await self._send_progress(
                    progress_queue,
                    DetectionState.COMPLETE,
                    f"Detection failed: {str(e)}",
                    git_url
                )
            
            return DetectionResult(
                repository_url=git_url,
                duration_seconds=duration,
                codebases=[],
                error=str(e)
            )
            
        finally:
            # Cancel heartbeat task
            if self._heartbeat_task and not self._heartbeat_task.done():
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
    
    async def _heartbeat_loop(self, progress_queue: asyncio.Queue, git_url: str) -> None:
        """
        Async heartbeat loop using asyncio.sleep (not threading.Timer).
        
        Follows asyncio best practices to avoid double-threading anti-pattern.
        
        Args:
            progress_queue: Queue for progress updates
            git_url: Repository URL being processed
        """
        try:
            while True:
                await asyncio.sleep(5.0)  # 5-second intervals as agreed
                
                progress = DetectionProgress(
                    state=DetectionState.ANALYZING,
                    message="Processing...",
                    repository_url=git_url
                )
                
                try:
                    # Non-blocking put
                    progress_queue.put_nowait(progress)
                except asyncio.QueueFull:
                    # Skip if queue is full
                    pass
                    
        except asyncio.CancelledError:
            # Proper cleanup on cancellation
            raise
    
    def _run_detector_with_progress(
        self,
        detector: PythonCodebaseDetector,
        git_url: str,
        progress_callback: Optional[Callable[[DetectionState, str], None]]
    ) -> List[CodebaseConfig]:
        """
        Run the detector with progress callbacks in the thread pool.
        
        This method runs in the ThreadPoolExecutor and uses thread-safe
        communication to send progress updates back to the main asyncio loop.
        
        Args:
            detector: PythonCodebaseDetector instance  
            git_url: GitHub repository URL or local path
            progress_callback: Optional progress callback function
            
        Returns:
            List of detected CodebaseConfig objects
        """
        if self.is_local:
            if progress_callback:
                progress_callback(DetectionState.ANALYZING, "Analyzing local repository...")
            
            # For local repos, git_url is actually a local path
            # Use detect_codebases_from_local_path method
            codebases = detector.detect_codebases_from_local_path(git_url)
        else:
            if progress_callback:
                progress_callback(DetectionState.CLONING, "Cloning repository...")
            
            # Use the existing detect_codebases method for remote repos
            codebases = detector.detect_codebases(git_url)
        
        return codebases
    
    def _create_thread_safe_progress_callback(
        self,
        loop: asyncio.AbstractEventLoop,
        progress_queue: asyncio.Queue,
        git_url: str
    ) -> Callable[[DetectionState, str], None]:
        """
        Create a thread-safe progress callback function.
        
        Uses asyncio.run_coroutine_threadsafe() for proper thread-safe 
        communication from ThreadPoolExecutor to the main event loop.
        
        Args:
            loop: The asyncio event loop
            progress_queue: Asyncio queue for progress updates
            git_url: Repository URL being processed
            
        Returns:
            Progress callback function that's thread-safe
        """
        def progress_callback(
            state: DetectionState,
            message: str
        ) -> None:
            """Thread-safe callback that runs in ThreadPoolExecutor"""
            # Create progress object
            progress = DetectionProgress(
                state=state,
                message=message,
                repository_url=git_url
            )
            
            # Create coroutine for async queue operation
            async def queue_put():
                try:
                    await progress_queue.put(progress)
                except asyncio.QueueFull:
                    # Skip if queue is full
                    pass
            
            # Schedule coroutine in event loop (thread-safe)
            try:
                asyncio.run_coroutine_threadsafe(queue_put(), loop)
            except RuntimeError:
                # Loop might be closed, ignore
                pass
        
        return progress_callback
    
    async def _send_progress(
        self,
        progress_queue: asyncio.Queue,
        state: DetectionState,
        message: str,
        git_url: str
    ) -> None:
        """
        Send progress update to the queue (async context).
        
        This runs in the main async context, not in ThreadPoolExecutor.
        
        Args:
            progress_queue: Queue for progress updates
            state: Current detection state
            message: Progress message
            git_url: Repository URL
        """
        try:
            progress = DetectionProgress(
                state=state,
                message=message,
                repository_url=git_url
            )
            
            # Use put() with timeout for backpressure handling
            await asyncio.wait_for(
                progress_queue.put(progress),
                timeout=1.0
            )
        except (asyncio.QueueFull, asyncio.TimeoutError):
            # Skip update if queue is full or timeout
            pass
    
    def cancel_detection(self, future: Future) -> None:
        """
        Cancel a running detection task.
        
        Follows asyncio best practices for cancellation - only cancels the
        Future but doesn't cleanup cloned repositories as agreed.
        
        Args:
            future: Future object representing the detection task
        """
        if future and not future.done():
            future.cancel()
        
        # Cancel heartbeat task if running
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()