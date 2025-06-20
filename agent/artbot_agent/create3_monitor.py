#!/usr/bin/env python3
"""
Create3 Robot Monitor Module
Monitors Create3 robot status using ROS2 for accurate battery and dock status
Based on the reference implementation in web_camera_viewer.py
"""

import os
import threading
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

# ROS2 imports for robot monitoring
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import BatteryState
    ROS2_AVAILABLE = True
    
    # Try to import Create3-specific messages
    try:
        from irobot_create_msgs.msg import DockStatus
        CREATE3_MSGS_AVAILABLE = True
    except ImportError:
        CREATE3_MSGS_AVAILABLE = False
        logger.warning("irobot_create_msgs not available - dock status monitoring disabled")
        
except ImportError:
    ROS2_AVAILABLE = False
    CREATE3_MSGS_AVAILABLE = False
    logger.warning("ROS2 not available - Create3 monitoring disabled")


class Create3Monitor(Node if ROS2_AVAILABLE else object):
    """ROS2 node for monitoring Create3 robot status"""
    
    def __init__(self, namespace=None):
        self.namespace = namespace or os.getenv('CREATE3_NAMESPACE', 'artbot1')
        self.connected = False
        self.last_update = None
        self.connection_timeout = 10  # seconds
        
        # Initialize status data
        self.battery_status = {
            'percentage': 0.0,
            'voltage': 0.0,
            'current': 0.0,
            'is_charging': False,
            'power_supply_status': 0,
            'temperature': 0.0,
            'last_update': None
        }
        
        self.dock_status = {
            'is_docked': False,
            'sees_dock': False,
            'last_update': None
        }
        
        if not ROS2_AVAILABLE:
            logger.error("ROS2 not available - Create3 monitoring will not work")
            return
            
        try:
            # Initialize ROS2 node
            super().__init__('artbot_create3_monitor')
            logger.info(f"🤖 Create3 monitor using namespace: {self.namespace}")
            
            # Create subscriber for battery status
            try:
                self.battery_status_sub = self.create_subscription(
                    BatteryState, 
                    f'/{self.namespace}/battery_state', 
                    self.battery_status_callback, 
                    qos_profile_sensor_data
                )
                logger.info(f"✅ Created battery status subscriber: /{self.namespace}/battery_state")
            except Exception as e:
                logger.error(f"❌ Failed to create battery status subscriber: {e}")
                self.battery_status_sub = None
            
            # Create subscriber for dock status (if available)
            if CREATE3_MSGS_AVAILABLE:
                try:
                    self.dock_status_sub = self.create_subscription(
                        DockStatus, 
                        f'/{self.namespace}/dock_status', 
                        self.dock_status_callback, 
                        qos_profile_sensor_data
                    )
                    logger.info(f"✅ Created dock status subscriber: /{self.namespace}/dock_status")
                except Exception as e:
                    logger.error(f"❌ Failed to create dock status subscriber: {e}")
                    self.dock_status_sub = None
            else:
                self.dock_status_sub = None
                logger.warning("⚠️  irobot_create_msgs not available - dock status disabled")
            
            logger.info("🤖 Create3 monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Create3 monitor: {e}")
    
    def battery_status_callback(self, msg):
        """Callback for battery status updates from Create3"""
        try:
            # Determine if charging based on multiple factors (from reference implementation)
            is_charging = False
            
            # Method 1: Check power_supply_status
            if msg.power_supply_status == 1:  # POWER_SUPPLY_STATUS_CHARGING
                is_charging = True
            elif msg.power_supply_status == 4:  # POWER_SUPPLY_STATUS_FULL
                is_charging = True
            elif msg.power_supply_status == 0:  # POWER_SUPPLY_STATUS_UNKNOWN
                # When status is unknown, use dock status and current as fallback
                if self.dock_status.get('is_docked', False):
                    # If docked, we assume charging is happening even with small discharge
                    # The Pi consumption can cause small negative current while still charging
                    if msg.current > -1.0:  # Less than 1A discharge (Pi typically uses ~0.3-0.5A)
                        is_charging = True
                    else:
                        # Strong negative current indicates discharging even when docked
                        is_charging = False
                else:
                    # Not docked, use current to determine
                    is_charging = msg.current > 0  # Positive current = charging
            
            # Update battery status
            self.battery_status = {
                'percentage': msg.percentage * 100,  # Convert to percentage (0-100)
                'voltage': msg.voltage,
                'current': msg.current,
                'is_charging': is_charging,
                'power_supply_status': msg.power_supply_status,
                'temperature': msg.temperature,
                'last_update': datetime.utcnow()
            }
            
            self.connected = True
            self.last_update = datetime.utcnow()
            
            logger.debug(f"🔋 Battery: {msg.percentage:.1%}, voltage={msg.voltage:.1f}V, "
                        f"current={msg.current:.3f}A, charging={is_charging}, "
                        f"docked={self.dock_status.get('is_docked', False)}")
            
        except Exception as e:
            logger.error(f"Error in battery status callback: {e}")
    
    def dock_status_callback(self, msg):
        """Callback for dock status updates from Create3"""
        try:
            self.dock_status = {
                'is_docked': msg.is_docked,
                'sees_dock': msg.dock_visible,
                'last_update': datetime.utcnow()
            }
            
            self.connected = True
            self.last_update = datetime.utcnow()
            
            logger.debug(f"🔔 Dock status: is_docked={msg.is_docked}, dock_visible={msg.dock_visible}")
            
        except Exception as e:
            logger.error(f"Error in dock status callback: {e}")
    
    def is_connected(self):
        """Check if Create3 is connected based on recent data"""
        if not self.last_update:
            return False
        
        # Consider connected if we received data within timeout period
        time_since_update = (datetime.utcnow() - self.last_update).total_seconds()
        return time_since_update < self.connection_timeout
    
    def get_status(self):
        """Get comprehensive Create3 status"""
        connected = self.is_connected()
        
        status = {
            'connected': connected,
            'battery_level': self.battery_status['percentage'],
            'battery_voltage': self.battery_status['voltage'],
            'battery_current': self.battery_status['current'],
            'is_charging': self.battery_status['is_charging'],
            'is_docked': self.dock_status['is_docked'],
            'sees_dock': self.dock_status['sees_dock'],
            'battery_temperature': self.battery_status['temperature'],
            'power_supply_status': self.battery_status['power_supply_status'],
            'last_battery_update': self.battery_status['last_update'].isoformat() if self.battery_status['last_update'] else None,
            'last_dock_update': self.dock_status['last_update'].isoformat() if self.dock_status['last_update'] else None,
            'namespace': self.namespace
        }
        
        if not connected:
            status['status'] = 'disconnected'
        elif self.dock_status['is_docked']:
            status['status'] = 'docked'
        elif self.battery_status['is_charging']:
            status['status'] = 'charging'
        else:
            status['status'] = 'active'
        
        return status


class Create3MonitorManager:
    """Manager for Create3 monitoring that handles ROS2 lifecycle"""
    
    def __init__(self):
        self.monitor = None
        self.ros_thread = None
        self.running = False
        self.namespace = os.getenv('CREATE3_NAMESPACE', 'artbot1')
        
    def start(self):
        """Start the Create3 monitor"""
        if not ROS2_AVAILABLE:
            logger.warning("ROS2 not available - Create3 monitoring disabled")
            return False
            
        if self.running:
            logger.warning("Create3 monitor already running")
            return True
            
        try:
            # Initialize ROS2 if not already done
            if not rclpy.ok():
                rclpy.init()
            
            # Create monitor instance
            self.monitor = Create3Monitor(self.namespace)
            
            # Start ROS2 spinning in separate thread
            self.running = True
            self.ros_thread = threading.Thread(target=self._ros_spin_thread, daemon=True)
            self.ros_thread.start()
            
            logger.info("✅ Create3 monitor started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Create3 monitor: {e}")
            self.running = False
            return False
    
    def stop(self):
        """Stop the Create3 monitor"""
        self.running = False
        
        if self.monitor:
            try:
                self.monitor.destroy_node()
            except Exception as e:
                logger.error(f"Error destroying Create3 monitor node: {e}")
            self.monitor = None
        
        if self.ros_thread and self.ros_thread.is_alive():
            self.ros_thread.join(timeout=2)
        
        logger.info("Create3 monitor stopped")
    
    def _ros_spin_thread(self):
        """ROS2 spinning thread"""
        try:
            while self.running and rclpy.ok():
                if self.monitor:
                    rclpy.spin_once(self.monitor, timeout_sec=0.1)
        except Exception as e:
            logger.error(f"Error in ROS2 spin thread: {e}")
        finally:
            self.running = False
    
    def get_status(self):
        """Get Create3 status"""
        if not self.monitor:
            return {
                'connected': False,
                'status': 'not_initialized',
                'battery_level': 0,
                'is_charging': False,
                'is_docked': False,
                'error': 'Monitor not initialized'
            }
        
        return self.monitor.get_status()
    
    def is_connected(self):
        """Check if Create3 is connected"""
        if not self.monitor:
            return False
        return self.monitor.is_connected()


# Global instance for the agent to use
create3_manager = Create3MonitorManager()


async def get_create3_status():
    """Async wrapper to get Create3 status"""
    try:
        return create3_manager.get_status()
    except Exception as e:
        logger.error(f"Error getting Create3 status: {e}")
        return {
            'connected': False,
            'status': 'error',
            'battery_level': 0,
            'is_charging': False,
            'is_docked': False,
            'error': str(e)
        }


def initialize_create3_monitoring():
    """Initialize Create3 monitoring"""
    logger.info("Initializing Create3 monitoring...")
    success = create3_manager.start()
    if success:
        logger.info("✅ Create3 monitoring initialized successfully")
    else:
        logger.error("❌ Failed to initialize Create3 monitoring")
    return success


def shutdown_create3_monitoring():
    """Shutdown Create3 monitoring"""
    logger.info("Shutting down Create3 monitoring...")
    create3_manager.stop()
