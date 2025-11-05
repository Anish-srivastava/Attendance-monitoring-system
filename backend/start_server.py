#!/usr/bin/env python3
"""
Enhanced Server Startup Script with Monitoring and Recovery
Provides automatic restart capabilities and resource monitoring
"""

import os
import sys
import time
import signal
import logging
import subprocess
import psutil
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServerManager:
    def __init__(self):
        self.process = None
        self.should_run = True
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_delay = 5  # seconds
        self.monitor_interval = 30  # seconds
        self.start_time = time.time()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.should_run = False
        if self.process:
            self.stop_server()
        sys.exit(0)
        
    def start_server(self):
        """Start the Flask server"""
        try:
            logger.info("Starting Flask server...")
            
            # Change to backend directory
            backend_dir = Path(__file__).parent
            os.chdir(backend_dir)
            
            # Start the server process
            self.process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            logger.info(f"Server started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
            
    def stop_server(self):
        """Stop the Flask server"""
        if self.process:
            try:
                logger.info("Stopping Flask server...")
                
                # Try graceful shutdown first
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    logger.warning("Graceful shutdown failed, force killing...")
                    self.process.kill()
                    self.process.wait()
                    
                logger.info("Server stopped")
                self.process = None
                
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
                
    def is_server_healthy(self):
        """Check if server is running and responsive"""
        if not self.process or self.process.poll() is not None:
            return False
            
        try:
            # Check if the process is still alive
            process = psutil.Process(self.process.pid)
            
            # Check memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb > 2048:  # More than 2GB
                logger.warning(f"High memory usage: {memory_mb:.1f} MB")
                
            # Check CPU usage
            cpu_percent = process.cpu_percent()
            if cpu_percent > 90:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                
            # TODO: Add HTTP health check to localhost:5000/health
            
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
            
    def monitor_server(self):
        """Monitor server health and restart if needed"""
        while self.should_run:
            try:
                if not self.is_server_healthy():
                    logger.error("Server is not healthy, attempting restart...")
                    self.restart_server()
                    
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring: {e}")
                time.sleep(5)
                
    def restart_server(self):
        """Restart the server"""
        if self.restart_count >= self.max_restarts:
            logger.error(f"Max restart attempts ({self.max_restarts}) reached. Exiting.")
            self.should_run = False
            return False
            
        self.restart_count += 1
        logger.info(f"Restarting server (attempt {self.restart_count}/{self.max_restarts})")
        
        # Stop current server
        self.stop_server()
        
        # Wait before restart
        time.sleep(self.restart_delay)
        
        # Start new server
        if self.start_server():
            logger.info("Server restarted successfully")
            return True
        else:
            logger.error("Failed to restart server")
            return False
            
    def run_with_monitoring(self):
        """Run server with monitoring and auto-restart"""
        logger.info("Starting server with monitoring...")
        
        # Start initial server
        if not self.start_server():
            logger.error("Failed to start initial server")
            return False
            
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_server, daemon=True)
        monitor_thread.start()
        
        # Main loop - monitor server output
        try:
            while self.should_run and self.process:
                # Read server output
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        print(line.strip())
                        
                        # Check for specific error patterns
                        if "Error" in line or "Exception" in line or "Traceback" in line:
                            logger.warning(f"Server error detected: {line.strip()}")
                            
                # Check if process has ended
                if self.process.poll() is not None:
                    logger.error("Server process ended unexpectedly")
                    if self.should_run:
                        self.restart_server()
                        
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.should_run = False
            
        finally:
            self.stop_server()
            
        uptime = time.time() - self.start_time
        logger.info(f"Server manager shutting down after {uptime/3600:.1f} hours")
        logger.info(f"Total restarts: {self.restart_count}")
        
    def run_simple(self):
        """Run server without monitoring (simple mode)"""
        logger.info("Starting server in simple mode...")
        
        if self.start_server():
            try:
                self.process.wait()
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            finally:
                self.stop_server()
        else:
            logger.error("Failed to start server")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Flask Server Manager')
    parser.add_argument('--simple', action='store_true', 
                       help='Run in simple mode without monitoring')
    parser.add_argument('--max-restarts', type=int, default=10,
                       help='Maximum number of restart attempts')
    parser.add_argument('--restart-delay', type=int, default=5,
                       help='Delay between restarts in seconds')
    
    args = parser.parse_args()
    
    manager = ServerManager()
    manager.max_restarts = args.max_restarts
    manager.restart_delay = args.restart_delay
    
    if args.simple:
        manager.run_simple()
    else:
        manager.run_with_monitoring()

if __name__ == "__main__":
    main()