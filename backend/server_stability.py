# server_stability.py - Server monitoring and crash recovery
import os
import sys
import time
import signal
import logging
import threading
import traceback
from functools import wraps
import gc

# Try to import psutil, fall back gracefully if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Resource monitoring will be limited.")

logger = logging.getLogger(__name__)

class ServerStabilityManager:
    """Manages server stability, monitoring, and recovery"""
    
    def __init__(self, app):
        self.app = app
        self.is_running = True
        self.start_time = time.time()
        self.error_count = 0
        self.last_error_time = 0
        self.memory_threshold = 1024 * 1024 * 1024  # 1GB
        self.monitoring_interval = 30  # seconds
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_resources, daemon=True)
        self.monitor_thread.start()
        
    def shutdown_handler(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.is_running = False
        self.cleanup_resources()
        sys.exit(0)
        
    def cleanup_resources(self):
        """Clean up resources before shutdown"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear any cached data
            if hasattr(self.app.config.get("MODEL_MANAGER"), 'cached_embeddings'):
                self.app.config.get("MODEL_MANAGER").cached_embeddings.clear()
                
            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            
    def monitor_resources(self):
        """Monitor system resources and log warnings"""
        if not PSUTIL_AVAILABLE:
            logger.warning("Resource monitoring disabled - psutil not available")
            return
            
        while self.is_running:
            try:
                # Monitor memory usage
                process = psutil.Process()
                memory_info = process.memory_info()
                
                if memory_info.rss > self.memory_threshold:
                    logger.warning(f"High memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
                    gc.collect()  # Force garbage collection
                    
                # Monitor CPU usage
                cpu_percent = process.cpu_percent()
                if cpu_percent > 80:
                    logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                    
                # Monitor file descriptors (Linux/Mac only)
                try:
                    if hasattr(process, 'num_fds'):
                        num_fds = process.num_fds()
                        if num_fds > 1000:
                            logger.warning(f"High file descriptor count: {num_fds}")
                except (AttributeError, psutil.NoSuchProcess):
                    pass  # Windows doesn't have num_fds
                    
                # Log uptime periodically
                uptime = time.time() - self.start_time
                if uptime % 3600 < self.monitoring_interval:  # Every hour
                    logger.info(f"Server uptime: {uptime/3600:.1f} hours, Errors: {self.error_count}")
                    
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                
            time.sleep(self.monitoring_interval)
            
    def log_error(self, error):
        """Log and track errors"""
        self.error_count += 1
        self.last_error_time = time.time()
        logger.error(f"Error #{self.error_count}: {error}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def stable_endpoint(func):
    """Decorator to make endpoints more stable with error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"Endpoint error in {func.__name__}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return a safe error response
            from flask import jsonify
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "message": "An error occurred processing your request. Please try again.",
                "endpoint": func.__name__
            }), 500
    return wrapper

def safe_memory_operation(func):
    """Decorator for memory-intensive operations with cleanup"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # Force garbage collection after memory-intensive operations
            gc.collect()
            return result
        except MemoryError:
            logger.error(f"Memory error in {func.__name__}")
            gc.collect()
            from flask import jsonify
            return jsonify({
                "success": False,
                "error": "Memory limit exceeded",
                "message": "Server is experiencing high memory usage. Please try again later."
            }), 503
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            gc.collect()
            raise
    return wrapper

# Context manager for resource management
class ManagedResource:
    """Context manager for proper resource cleanup"""
    def __init__(self, resource_name):
        self.resource_name = resource_name
        self.start_time = time.time()
        
    def __enter__(self):
        logger.debug(f"Acquiring resource: {self.resource_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            logger.error(f"Error with resource {self.resource_name}: {exc_val}")
        else:
            logger.debug(f"Released resource {self.resource_name} after {duration:.2f}s")
        
        # Force cleanup
        gc.collect()
        return False  # Don't suppress exceptions