#!/usr/bin/env python3
"""
Web-based Camera Viewer with Distance Detection and Robot Control
View camera feed and person detections with distance measurement through web browser
Control Create 3 robot with keyboard arrows
"""

import os
import time
import threading
import base64
import cv2
import numpy as np
import depthai as dai
from flask import Flask, render_template_string, Response, jsonify, request
import json
import psutil
import subprocess

# ROS2 imports for robot control
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from std_msgs.msg import Bool
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    print("⚠️  ROS2 not available - robot control disabled")

app = Flask(__name__)

# Global variables for camera data
camera_frame = None
detection_data = []
camera_active = False
camera_error = None
camera_running = True  # Track if camera should be running
camera_device = None  # Global camera device instance

# Robot control variables
robot_control_active = False
current_movement = {'linear': 0.0, 'angular': 0.0}
movement_speed = 0.15  # m/s
turn_speed = 0.3      # rad/s
robot_node = None

class PowerMonitor:
    """Monitor OAK-D power consumption and system resources"""
    
    def __init__(self):
        self.power_data = {
            'temperature': None,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'usb_power_info': {
                'status': 'Unknown',
                'note': 'Checking...',
                'sysfs_power': None,
                'device_type': 'Unknown'
            },
            'oakd_monitoring': {
                'chip_temp': None,
                'css_cpu': None,
                'mss_cpu': None,
                'css_memory': None,
                'ddr_memory': None,
                'usb_speed': None,
                'device_name': None,
                'mxid': None
            },
            'device_state': 'Unknown',
            'device_info': None,
            'last_update': None
        }
    
    def get_usb_power(self):
        """Get USB power information for OAK-D camera"""
        try:
            # Check if OAK-D is connected by looking for the device ID
            oakd_check = subprocess.run(
                "lsusb | grep '03e7:2485'", 
                shell=True, capture_output=True, text=True
            )
            
            # Check sysfs power info first
            oakd_paths = [
                "/sys/bus/usb/devices/1-1.1/bMaxPower",
                "/sys/bus/usb/devices/1-1/bMaxPower", 
                "/sys/bus/usb/devices/2-1/bMaxPower",
                "/sys/bus/usb/devices/3-1/bMaxPower"
            ]
            
            sysfs_power = None
            for path in oakd_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        power_str = f.read().strip()
                        if 'mA' in power_str:
                            sysfs_power = power_str
                            break
            
            # If we found power info in sysfs, OAK-D is connected
            if sysfs_power:
                # Default for OAK-D based on known specifications
                power_status = "OAK-D Lite (up to 1.2A)"
                power_note = "Self-powered device, can exceed USB limits"
                device_type = "OAK-D Lite"
            elif oakd_check.returncode == 0:
                # Device found in lsusb but no sysfs power info
                power_status = "OAK-D Lite (up to 1.2A)"
                power_note = "Device detected, power info unavailable"
                device_type = "OAK-D Lite"
            else:
                # No device found
                return {
                    'status': 'OAK-D Not Found',
                    'note': 'Device not connected or not detected',
                    'sysfs_power': None,
                    'device_type': 'Unknown'
                }
            
            return {
                'status': power_status,
                'note': power_note,
                'sysfs_power': sysfs_power,
                'device_type': device_type
            }
            
        except Exception as e:
            return {
                'status': 'Error',
                'note': f'Detection failed: {str(e)[:50]}...',
                'sysfs_power': None,
                'device_type': 'Unknown'
            }
    
    def get_device_info(self):
        """Get OAK-D device information"""
        try:
            # Try to get device info from sysfs
            device_paths = [
                "/sys/bus/usb/devices/1-1.1",
                "/sys/bus/usb/devices/1-1",
                "/sys/bus/usb/devices/2-1",
                "/sys/bus/usb/devices/3-1"
            ]
            
            for path in device_paths:
                if os.path.exists(path):
                    # Check if this is the OAK-D device
                    try:
                        with open(f"{path}/idVendor", 'r') as f:
                            vendor_id = f.read().strip()
                        with open(f"{path}/idProduct", 'r') as f:
                            product_id = f.read().strip()
                        
                        # OAK-D vendor/product IDs
                        if vendor_id == "03e7" and product_id == "2485":
                            return {
                                'vendor_id': vendor_id,
                                'product_id': product_id,
                                'path': path
                            }
                    except:
                        continue
        except Exception as e:
            print(f"Device info error: {e}")
        return None
    
    def get_device_temperature(self):
        """Get OAK-D device temperature if available"""
        try:
            # Try to read temperature from device
            result = subprocess.run(['cat', '/sys/class/thermal/thermal_zone0/temp'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                temp = float(result.stdout.strip()) / 1000.0
                return temp
        except:
            pass
        return None
    
    def update_power_data(self):
        """Update power monitoring data"""
        self.power_data['cpu_usage'] = psutil.cpu_percent(interval=1)
        self.power_data['memory_usage'] = psutil.virtual_memory().percent
        self.power_data['usb_power_info'] = self.get_usb_power()
        self.power_data['oakd_monitoring'] = self.get_oakd_monitoring()
        self.power_data['temperature'] = self.get_device_temperature()
        self.power_data['device_state'] = 'Active' if camera_active else 'Inactive'
        self.power_data['device_info'] = self.get_device_info()
        self.power_data['last_update'] = time.strftime('%H:%M:%S')
    
    def get_power_data(self):
        """Get current power data"""
        return self.power_data

    def get_oakd_monitoring(self):
        """Get OAK-D internal monitoring data"""
        global camera_device
        
        try:
            # Use global camera device if available, otherwise create new one
            device = None
            if camera_device and camera_active:
                device = camera_device
            else:
                try:
                    device = dai.Device()
                except Exception as e:
                    return {
                        'chip_temp': None,
                        'css_cpu': None,
                        'mss_cpu': None,
                        'css_memory': None,
                        'ddr_memory': None,
                        'usb_speed': None,
                        'device_name': None,
                        'mxid': None,
                        'error': f'Device not available: {str(e)}'
                    }
            
            if not device:
                return {
                    'chip_temp': None,
                    'css_cpu': None,
                    'mss_cpu': None,
                    'css_memory': None,
                    'ddr_memory': None,
                    'usb_speed': None,
                    'device_name': None,
                    'mxid': None,
                    'error': 'Could not access device'
                }
            
            # Get chip temperature
            temp = device.getChipTemperature()
            
            # Get CPU usage
            css_cpu = device.getLeonCssCpuUsage()
            mss_cpu = device.getLeonMssCpuUsage()
            
            # Get memory usage
            css_mem = device.getCmxMemoryUsage()
            ddr_mem = device.getDdrMemoryUsage()
            
            # Get USB speed
            usb_speed = device.getUsbSpeed()
            
            # Get device info
            device_info = device.getDeviceInfo()
            
            return {
                'chip_temp': temp.average if temp else None,
                'css_cpu': css_cpu.average if hasattr(css_cpu, 'average') else css_cpu,
                'mss_cpu': mss_cpu.average if hasattr(mss_cpu, 'average') else mss_cpu,
                'css_memory_used': css_mem.used if hasattr(css_mem, 'used') else css_mem,
                'css_memory_total': css_mem.total if hasattr(css_mem, 'total') else None,
                'css_memory_percent': (css_mem.used / css_mem.total * 100) if hasattr(css_mem, 'used') and hasattr(css_mem, 'total') and css_mem.total > 0 else None,
                'ddr_memory_used': ddr_mem.used if hasattr(ddr_mem, 'used') else ddr_mem,
                'ddr_memory_total': ddr_mem.total if hasattr(ddr_mem, 'total') else None,
                'ddr_memory_percent': (ddr_mem.used / ddr_mem.total * 100) if hasattr(ddr_mem, 'used') and hasattr(ddr_mem, 'total') and ddr_mem.total > 0 else None,
                'usb_speed': str(usb_speed) if usb_speed else None,
                'device_name': device_info.name if device_info else None,
                'mxid': device_info.mxid if device_info else None,
                'error': None
            }
            
        except Exception as e:
            return {
                'chip_temp': None,
                'css_cpu': None,
                'mss_cpu': None,
                'css_memory': None,
                'ddr_memory': None,
                'usb_speed': None,
                'device_name': None,
                'mxid': None,
                'error': str(e)
            }

class RobotController(Node):
    """ROS2 node for robot control"""
    
    def __init__(self):
        super().__init__('web_robot_controller')
        
        # Get namespace from environment variable
        self.namespace = os.getenv('CREATE3_NAMESPACE', 'artbot1')
        print(f"🤖 Robot controller using namespace: {self.namespace}")
        
        # Create publisher for movement commands
        try:
            self.cmd_vel_pub = self.create_publisher(
                Twist, f'/{self.namespace}/cmd_vel', 10
            )
            print(f"✅ Created cmd_vel publisher for /{self.namespace}/cmd_vel")
        except Exception as e:
            print(f"❌ Failed to create cmd_vel publisher: {e}")
            self.cmd_vel_pub = None
        
        # Initialize safety-related attributes
        self.safety_pub = None  # Initialize to None to avoid AttributeError
        self.safety_enabled = True
        
        # Create action clients for docking
        try:
            from rclpy.action import ActionClient
            from irobot_create_msgs.action import Dock, Undock
            
            self.dock_client = ActionClient(self, Dock, f'/{self.namespace}/dock')
            self.undock_client = ActionClient(self, Undock, f'/{self.namespace}/undock')
            print(f"✅ Created docking action clients")
        except ImportError:
            print("⚠️  irobot_create_msgs not available - docking disabled")
            self.dock_client = None
            self.undock_client = None
        except Exception as e:
            print(f"❌ Failed to create docking action clients: {e}")
            self.dock_client = None
            self.undock_client = None
        
        # Create subscriber for dock status
        try:
            from irobot_create_msgs.msg import DockStatus
            from rclpy.qos import qos_profile_sensor_data
            self.dock_status_sub = self.create_subscription(
                DockStatus, f'/{self.namespace}/dock_status', self.dock_status_callback, qos_profile_sensor_data
            )
            self.dock_status = {'is_docked': False, 'sees_dock': False}
            print(f"✅ Created dock status subscriber with qos_profile_sensor_data")
        except ImportError:
            print("⚠️  irobot_create_msgs not available - dock status disabled")
            self.dock_status_sub = None
            self.dock_status = {'is_docked': False, 'sees_dock': False}
        except Exception as e:
            print(f"❌ Failed to create dock status subscriber: {e}")
            self.dock_status_sub = None
            self.dock_status = {'is_docked': False, 'sees_dock': False}
        
        # Create subscriber for battery status
        try:
            from sensor_msgs.msg import BatteryState
            self.battery_status_sub = self.create_subscription(
                BatteryState, f'/{self.namespace}/battery_state', self.battery_status_callback, qos_profile_sensor_data
            )
            self.battery_status = {
                'percentage': 0.0,
                'voltage': 0.0,
                'is_charging': False,
                'power_supply_status': 0,
                'temperature': 0.0
            }
            print(f"✅ Created battery status subscriber with qos_profile_sensor_data")
        except ImportError:
            print("⚠️  sensor_msgs not available - battery status disabled")
            self.battery_status_sub = None
            self.battery_status = {
                'percentage': 0.0,
                'voltage': 0.0,
                'is_charging': False,
                'power_supply_status': 0,
                'temperature': 0.0
            }
        except Exception as e:
            print(f"❌ Failed to create battery status subscriber: {e}")
            self.battery_status_sub = None
            self.battery_status = {
                'percentage': 0.0,
                'voltage': 0.0,
                'is_charging': False,
                'power_supply_status': 0,
                'temperature': 0.0
            }
        
        print("🤖 Robot controller initialized")
    
    def dock_status_callback(self, msg):
        """Callback for dock status updates"""
        print(f"🔔 Dock status callback: is_docked={msg.is_docked}, dock_visible={msg.dock_visible}")
        self.dock_status = {
            'is_docked': msg.is_docked,
            'sees_dock': msg.dock_visible
        }
        print(f"📝 Updated dock_status: {self.dock_status}")
    
    def battery_status_callback(self, msg):
        """Callback for battery status updates"""
        # Determine if charging based on multiple factors
        is_charging = False
        
        # Method 1: Check power_supply_status
        if msg.power_supply_status == 1:  # POWER_SUPPLY_STATUS_CHARGING
            is_charging = True
        elif msg.power_supply_status == 4:  # POWER_SUPPLY_STATUS_FULL
            is_charging = True
        elif msg.power_supply_status == 0:  # POWER_SUPPLY_STATUS_UNKNOWN
            # When status is unknown, use dock status and current as fallback
            if hasattr(self, 'dock_status') and self.dock_status.get('is_docked', False):
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
        
        print(f"🔋 Battery status callback: percentage={msg.percentage:.1%}, voltage={msg.voltage:.1f}V, current={msg.current:.3f}A, charging={is_charging}, docked={getattr(self, 'dock_status', {}).get('is_docked', False)}")
        
        self.battery_status = {
            'percentage': msg.percentage,
            'voltage': msg.voltage,
            'current': msg.current,
            'is_charging': is_charging,
            'power_supply_status': msg.power_supply_status,
            'temperature': msg.temperature
        }
        print(f"📝 Updated battery_status: {self.battery_status}")
    
    def get_dock_status(self):
        """Get current dock status"""
        print(f"🔍 get_dock_status called, returning: {self.dock_status}")
        return self.dock_status
    
    def get_battery_status(self):
        """Get current battery status"""
        print(f"🔍 get_battery_status called, returning: {self.battery_status}")
        return self.battery_status
    
    def send_dock_command(self):
        """Send dock command to robot"""
        if not self.dock_client:
            return False, "Docking not available"
        
        try:
            # Check if already docked
            if self.dock_status.get('is_docked', False):
                return False, "Robot is already docked"
            
            # Create and send dock goal
            from irobot_create_msgs.action import Dock
            goal = Dock.Goal()
            self.dock_client.send_goal_async(goal)
            print("🤖 Dock command sent")
            return True, "Dock command sent successfully"
        except Exception as e:
            print(f"❌ Error sending dock command: {e}")
            return False, f"Dock command failed: {e}"
    
    def send_undock_command(self):
        """Send undock command to robot"""
        if not self.undock_client:
            return False, "Undocking not available"
        
        try:
            # Check if already undocked
            if not self.dock_status.get('is_docked', False):
                return False, "Robot is already undocked"
            
            # Create and send undock goal
            from irobot_create_msgs.action import Undock
            goal = Undock.Goal()
            self.undock_client.send_goal_async(goal)
            print("🤖 Undock command sent")
            return True, "Undock command sent successfully"
        except Exception as e:
            print(f"❌ Error sending undock command: {e}")
            return False, f"Undock command failed: {e}"
    
    def send_movement(self, linear_speed, angular_speed):
        """Send movement command to robot"""
        if not self.cmd_vel_pub:
            print("❌ No cmd_vel publisher available")
            return False
        
        try:
            # Create Twist message with proper float values
            twist = Twist()
            twist.linear.x = float(linear_speed)
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = float(angular_speed)
            
            # Publish the command
            self.cmd_vel_pub.publish(twist)
            print(f"🤖 Movement command sent: linear={linear_speed:.2f}, angular={angular_speed:.2f}")
            
            # Publish safety status if available
            if self.safety_pub:
                try:
                    safety_msg = Bool()
                    safety_msg.data = self.safety_enabled
                    self.safety_pub.publish(safety_msg)
                except Exception as e:
                    print(f"⚠️ Failed to publish safety status: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending movement command: {e}")
            return False
    
    def stop_robot(self):
        """Stop robot movement"""
        return self.send_movement(0.0, 0.0)
    
    def enable_safety(self, enabled=True):
        """Enable or disable safety constraints"""
        self.safety_enabled = enabled
        print(f"🛡️ Safety {'enabled' if enabled else 'disabled'}")

def init_robot_control():
    """Initialize ROS2 robot control"""
    global robot_node, robot_control_active
    
    if not ROS2_AVAILABLE:
        print("⚠️  ROS2 not available - robot control disabled")
        return False
    
    try:
        # Set ROS environment variables
        os.environ.setdefault('ROS_DOMAIN_ID', '1')
        os.environ.setdefault('RMW_IMPLEMENTATION', 'rmw_cyclonedds_cpp')
        os.environ.setdefault('CREATE3_NAMESPACE', 'artbot1')
        
        print(f"🔧 ROS Environment: DOMAIN_ID={os.environ.get('ROS_DOMAIN_ID')}, RMW={os.environ.get('RMW_IMPLEMENTATION')}")
        
        # Initialize ROS2 if not already done
        if not rclpy.ok():
            rclpy.init()
            print("✅ ROS2 initialized")
        
        # Create robot controller node
        robot_node = RobotController()
        robot_control_active = True
        
        # Start ROS2 spinning in a separate thread
        def spin_ros():
            print("[SPIN_THREAD] ROS2 spin thread started.")
            try:
                print("[SPIN_THREAD] Calling rclpy.spin(robot_node)...")
                rclpy.spin(robot_node)
                print("[SPIN_THREAD] rclpy.spin() exited normally.")
            except KeyboardInterrupt:
                print("[SPIN_THREAD] ROS2 spin interrupted by KeyboardInterrupt.")
            except Exception as e:
                print(f"[SPIN_THREAD] ❌ ROS2 spin error: {e}")
            finally:
                print("[SPIN_THREAD] Spin thread exiting.")
        
        threading.Thread(target=spin_ros, daemon=True).start()
        
        print("✅ Robot control initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize robot control: {e}")
        robot_control_active = False
        return False

# Create power monitor instance
power_monitor = PowerMonitor()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Camera Viewer with Distance Detection & Robot Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1400px; margin: 0 auto; }
        .camera-feed { text-align: center; margin: 20px 0; }
        .camera-feed img { max-width: 100%; border: 2px solid #333; border-radius: 8px; }
        .status { background: #fff; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .detection-info { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .power-info { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .robot-control { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .controls { background: #fff; padding: 15px; border-radius: 8px; margin: 10px 0; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        .error { background: #ffe6e6; color: #d32f2f; padding: 10px; border-radius: 5px; }
        .success { background: #e8f5e8; color: #2e7d32; padding: 10px; border-radius: 5px; }
        .distance-highlight { background: #fff3cd; border-left: 4px solid #ffc107; }
        .distance-warning { background: #f8d7da; border-left: 4px solid #dc3545; }
        .distance-ideal { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .full-width { grid-column: 1 / -1; }
        .power-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
        .power-item { background: #fff; padding: 10px; border-radius: 5px; text-align: center; }
        .power-value { font-size: 18px; font-weight: bold; margin: 5px 0; }
        .power-label { font-size: 12px; color: #666; }
        .temp-good { color: #4CAF50; }
        .temp-warning { color: #FF9800; }
        .temp-danger { color: #F44336; }
        .power-note {
            font-size: 0.8em;
            color: #666;
            margin-top: 2px;
            font-style: italic;
        }
        .robot-status {
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #28a745;
        }
        .keyboard-hint {
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 14px;
            color: #495057;
        }
        .movement-display {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 14px;
        }
        .speed-control {
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        .speed-slider {
            width: 100%;
            margin: 10px 0;
        }
        .speed-value {
            font-weight: bold;
            color: #007bff;
        }
        .docking-control {
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #28a745;
        }
        .dock-status {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 14px;
        }
        .dock-buttons {
            display: flex;
            gap: 10px;
            margin: 10px 0;
            flex-wrap: wrap;
        }
        .dock-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        .dock-btn:hover {
            background: #0056b3;
        }
        .dock-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        .dock-message {
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 14px;
            min-height: 20px;
        }
        .battery-status {
            background: #e8f5e8;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 14px;
            border-left: 3px solid #28a745;
        }
        .battery-status.charging {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        .battery-status.low {
            background: #f8d7da;
            border-left-color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Robot Camera Viewer with Distance Detection & Robot Control</h1>
        
        <div class="grid">
        <div class="status">
            <h3>📊 Status</h3>
                <p>Camera Running: <span id="camera-running-status">Checking...</span></p>
            <p>Camera Active: <span id="camera-status">Checking...</span></p>
            <p>FPS: <span id="fps">--</span></p>
            <p>Detections: <span id="detection-count">0</span></p>
            <p>Error: <span id="error-message">None</span></p>
        </div>
        
            <div class="status">
                <h3>📏 Distance Analysis</h3>
                <p>Closest Person: <span id="closest-distance">--</span></p>
                <p>Average Distance: <span id="avg-distance">--</span></p>
                <p>Detection Quality: <span id="detection-quality">--</span></p>
            </div>
        </div>
        
        <div class="robot-control full-width">
            <h3>🎮 Robot Control</h3>
            <div class="robot-status">
                <p><strong>Robot Control Status:</strong> <span id="robot-control-status">Checking...</span></p>
                <p><strong>ROS2 Available:</strong> <span id="ros2-status">Checking...</span></p>
                <p><strong>Current Movement:</strong> <span id="current-movement">Stopped</span></p>
            </div>
            
            <div class="keyboard-hint">
                <strong>🎹 Keyboard Controls:</strong> Hold arrow keys to move continuously
                <br>↑ Forward | ↓ Backward | ← Left Turn | → Right Turn | Space Stop
                <br><em>Combine keys for diagonal movement: ↑+→ Forward+Right, ↓+← Backward+Left, etc.</em>
                <br><em>Speed reduced by 40% for better control</em>
            </div>
            
            <div class="speed-control">
                <h4>⚡ Speed Control</h4>
                <p><strong>Current Speed Multiplier:</strong> <span id="speed-multiplier" class="speed-value">100%</span></p>
                <input type="range" id="speed-slider" class="speed-slider" min="20" max="150" value="100" step="10">
                <p><small>20% (Very Slow) ← → 150% (Fast)</small></p>
            </div>
            
            <div class="docking-control">
                <h4>🔋 Docking Control</h4>
                <div class="dock-status">
                    <p><strong>Dock Status:</strong> <span id="dock-status">Checking...</span></p>
                    <p><strong>Sees Dock:</strong> <span id="sees-dock">Checking...</span></p>
                </div>
                <div class="battery-status">
                    <p><strong>Battery:</strong> <span id="battery-percentage">--</span>% <span id="battery-voltage">(--V)</span></p>
                    <p><strong>Current:</strong> <span id="battery-current">--A</span></p>
                    <p><strong>Charging:</strong> <span id="battery-charging">--</span></p>
                    <p><strong>Temperature:</strong> <span id="battery-temperature">--°C</span></p>
                </div>
                <div class="dock-buttons">
                    <button id="dock-btn" class="dock-btn" onclick="sendDockCommand()">🚀 Dock</button>
                    <button id="undock-btn" class="dock-btn" onclick="sendUndockCommand()">🔌 Undock</button>
                    <button id="refresh-dock-btn" class="dock-btn" onclick="refreshDockStatus()">🔄 Refresh Status</button>
                </div>
                <div id="dock-message" class="dock-message"></div>
            </div>
            
            <div class="movement-display">
                <strong>Movement Display:</strong> <span id="movement-display">Linear: 0.00 m/s, Angular: 0.00 rad/s</span>
            </div>
        </div>
        
        <div class="power-info full-width">
            <h3>🔋 Power & System Monitoring</h3>
            <div class="power-grid">
                <div class="power-item">
                    <div class="power-label">Pi Temperature</div>
                    <div class="power-value" id="temperature">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">Pi CPU Usage</div>
                    <div class="power-value" id="cpu-usage">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">Pi Memory Usage</div>
                    <div class="power-value" id="memory-usage">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">OAK-D Chip Temp</div>
                    <div class="power-value" id="oakd-temp">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">OAK-D CSS CPU</div>
                    <div class="power-value" id="oakd-css-cpu">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">OAK-D MSS CPU</div>
                    <div class="power-value" id="oakd-mss-cpu">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">OAK-D CSS Memory</div>
                    <div class="power-value" id="oakd-css-mem">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">OAK-D DDR Memory</div>
                    <div class="power-value" id="oakd-ddr-mem">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">USB Speed</div>
                    <div class="power-value" id="usb-speed">--</div>
                </div>
                <div class="power-item">
                    <div class="power-label">Device State</div>
                    <div class="power-value" id="device-state">--</div>
                </div>
            </div>
            <div class="power-note">
                <strong>OAK-D Internal Monitoring:</strong> Real-time chip temperature, CPU usage (CSS/MSS), and memory usage from the MyriadX processor
            </div>
        </div>
        
        <div class="camera-feed full-width">
            <h3>📷 Camera Feed with Distance Detection</h3>
            <img id="camera-image" src="/video_feed" alt="Camera Feed" style="display: none;">
            <div id="no-feed" style="padding: 50px; background: #ddd; border-radius: 8px;">
                <p>No camera feed available</p>
            </div>
        </div>
        
        <div class="detection-info full-width">
            <h3>👤 Person Detections with Distance</h3>
            <div id="detections-list">
                <p>No detections yet...</p>
            </div>
        </div>
        
        <div class="controls full-width">
            <h3>🎮 Controls</h3>
            <button onclick="refreshPage()">🔄 Refresh</button>
            <button onclick="toggleFullscreen()">📺 Fullscreen</button>
            <button onclick="captureImage()">📸 Capture Image</button>
            <button onclick="restartCamera()">🔄 Restart Camera</button>
            <button onclick="saveDetectionFrame()">💾 Save Detection Frame</button>
            <button id="camera-toggle-btn" onclick="toggleCamera()" style="background: #28a745;">📷 Start Camera</button>
        </div>
    </div>

    <script>
        let frameCount = 0;
        let lastTime = Date.now();
        let robotControlActive = false;
        let currentMovement = {linear: 0.0, angular: 0.0};
        let keyStates = {}; // Track which keys are currently pressed
        let movementInterval = null; // For continuous movement
        let speedMultiplier = 1.0; // Speed multiplier (100% = 1.0)
        
        // Base movement speeds (reduced by 40%)
        const BASE_MOVEMENT_SPEEDS = {
            forward: 0.18,    // m/s (was 0.30)
            backward: -0.18,  // m/s (was -0.30)
            turn: 0.48        // rad/s (was 0.80)
        };
        
        // Get current movement speeds with multiplier
        function getCurrentSpeeds() {
            return {
                forward: BASE_MOVEMENT_SPEEDS.forward * speedMultiplier,
                backward: BASE_MOVEMENT_SPEEDS.backward * speedMultiplier,
                turn: BASE_MOVEMENT_SPEEDS.turn * speedMultiplier
            };
        }
        
        // Robot control functions
        function sendMovement(linear, angular) {
            fetch('/robot_control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    linear: linear,
                    angular: angular
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentMovement = {linear: linear, angular: angular};
                    updateMovementDisplay();
                } else {
                    console.error('Robot control failed:', data.error);
                }
            })
            .catch(error => {
                console.error('Robot control error:', error);
            });
        }
        
        function stopRobot() {
            sendMovement(0.0, 0.0);
        }
        
        function updateMovementDisplay() {
            const speeds = getCurrentSpeeds();
            document.getElementById('current-movement').innerHTML = 
                `Linear: ${currentMovement.linear.toFixed(2)} m/s, Angular: ${currentMovement.angular.toFixed(2)} rad/s<br>` +
                `<small>Max Forward: ${speeds.forward.toFixed(2)} m/s, Max Turn: ${speeds.turn.toFixed(2)} rad/s</small>`;
            
            // Update speed display
            document.getElementById('speed-multiplier').textContent = Math.round(speedMultiplier * 100) + '%';
        }
        
        function startMovementUpdates() {
            if (movementInterval) return;
            
            movementInterval = setInterval(() => {
                let linear = 0.0;
                let angular = 0.0;
                const speeds = getCurrentSpeeds();
                const currentTime = Date.now();
                
                // Calculate movement based on pressed keys
                // Forward/Backward combinations
                if (keyStates['ArrowUp']) {
                    linear += speeds.forward;
                }
                if (keyStates['ArrowDown']) {
                    linear += speeds.backward;
                }
                
                // Left/Right combinations
                if (keyStates['ArrowLeft']) {
                    angular += speeds.turn;
                }
                if (keyStates['ArrowRight']) {
                    angular -= speeds.turn;
                }
                
                // Send the combined movement command
                sendMovement(linear, angular);
            }, 50); // Update every 50ms for smooth movement
        }
        
        function stopMovementUpdates() {
            if (movementInterval) {
                clearInterval(movementInterval);
                movementInterval = null;
            }
        }
        
        // Keyboard event handling
        document.addEventListener('keydown', function(event) {
            if (!robotControlActive) return;
            
            const key = event.key;
            
            // Handle arrow keys and space
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(key)) {
                event.preventDefault();
                
                // Handle space key for immediate stop
                if (key === ' ') {
                    stopRobot();
                    keyStates = {}; // Clear all key states
                    stopMovementUpdates();
                    return;
                }
                
                // Mark key as pressed
                keyStates[key] = true;
                
                // Start movement updates if not already running
                if (!movementInterval) {
                    startMovementUpdates();
                }
            }
        });
        
        document.addEventListener('keyup', function(event) {
            if (!robotControlActive) return;
            
            const key = event.key;
            
            // Only handle arrow keys
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
                event.preventDefault();
                
                // Mark key as released
                delete keyStates[key];
                
                // If no keys are pressed, stop movement updates
                if (Object.keys(keyStates).length === 0) {
                    stopMovementUpdates();
                    stopRobot();
                }
            }
        });
        
        // Cleanup when page loses focus
        document.addEventListener('blur', function() {
            if (robotControlActive) {
                keyStates = {};
                stopMovementUpdates();
                stopRobot();
            }
        });
        
        // Cleanup when page is unloaded
        window.addEventListener('beforeunload', function() {
            if (robotControlActive) {
                keyStates = {};
                stopMovementUpdates();
                stopRobot();
            }
        });
        
        // Update robot status
        function updateRobotStatus() {
            fetch('/robot_status')
                .then(response => response.json())
                .then(data => {
                    robotControlActive = data.robot_control_active;
                    currentMovement = data.current_movement;
                    
                    document.getElementById('robot-control-status').textContent = 
                        data.robot_control_active ? 'Active' : 'Inactive';
                    document.getElementById('ros2-status').textContent = 
                        data.ros2_available ? 'Available' : 'Not Available';
                    
                    const movementText = data.current_movement.linear === 0 && data.current_movement.angular === 0 
                        ? 'Stopped' 
                        : `Moving (${data.current_movement.linear.toFixed(2)}, ${data.current_movement.angular.toFixed(2)})`;
                    document.getElementById('current-movement').textContent = movementText;
                    
                    updateMovementDisplay();
                })
                .catch(error => {
                    console.error('Error fetching robot status:', error);
                });
        }
        
        // Update camera feed
        function updateCameraFeed() {
            const img = document.getElementById('camera-image');
            const noFeed = document.getElementById('no-feed');
            
            img.onload = function() {
                img.style.display = 'block';
                noFeed.style.display = 'none';
                frameCount++;
                
                // Calculate FPS
                const now = Date.now();
                if (now - lastTime >= 1000) {
                    document.getElementById('fps').textContent = frameCount;
                    frameCount = 0;
                    lastTime = now;
                }
            };
            
            img.onerror = function() {
                img.style.display = 'none';
                noFeed.style.display = 'block';
            };
            
            // Refresh image every 100ms
            img.src = '/video_feed?' + new Date().getTime();
        }
        
        // Update detection data
        function updateDetections() {
            fetch('/detections')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('camera-status').textContent = data.camera_active ? 'Active' : 'Inactive';
                    document.getElementById('detection-count').textContent = data.detections.length;
                    document.getElementById('error-message').textContent = data.error || 'None';
                    
                    // Update distance analysis
                    if (data.detections.length > 0) {
                        const distances = data.detections.map(d => d.distance).filter(d => d !== null);
                        if (distances.length > 0) {
                            const closest = Math.min(...distances);
                            const avg = distances.reduce((a, b) => a + b, 0) / distances.length;
                            document.getElementById('closest-distance').textContent = closest.toFixed(2) + 'm';
                            document.getElementById('avg-distance').textContent = avg.toFixed(2) + 'm';
                            
                            // Detection quality based on distance
                            if (closest >= 0.5 && closest <= 2.0) {
                                document.getElementById('detection-quality').textContent = '🟢 Ideal Range';
                            } else if (closest < 0.5) {
                                document.getElementById('detection-quality').textContent = '🟡 Too Close';
                            } else {
                                document.getElementById('detection-quality').textContent = '🔴 Too Far';
                            }
                        } else {
                            document.getElementById('closest-distance').textContent = 'No depth data';
                            document.getElementById('avg-distance').textContent = 'No depth data';
                            document.getElementById('detection-quality').textContent = '⚠️ No depth';
                        }
                    } else {
                        document.getElementById('closest-distance').textContent = '--';
                        document.getElementById('avg-distance').textContent = '--';
                        document.getElementById('detection-quality').textContent = '--';
                    }
                    
                    const detectionsList = document.getElementById('detections-list');
                    if (data.detections.length === 0) {
                        detectionsList.innerHTML = '<p>No detections yet...</p>';
                    } else {
                        let html = '';
                        data.detections.forEach((det, index) => {
                            let distanceClass = '';
                            if (det.distance !== null) {
                                if (det.distance >= 0.5 && det.distance <= 2.0) {
                                    distanceClass = 'distance-ideal';
                                } else if (det.distance < 0.5) {
                                    distanceClass = 'distance-warning';
                                } else {
                                    distanceClass = 'distance-highlight';
                                }
                            }
                            
                            html += `
                                <div style="background: #fff; padding: 15px; margin: 8px 0; border-radius: 8px; border-left: 4px solid #4caf50;" class="${distanceClass}">
                                    <strong>Person ${index + 1}</strong><br>
                                    <strong>Confidence:</strong> ${(det.confidence * 100).toFixed(1)}%<br>
                                    <strong>Distance:</strong> ${det.distance ? det.distance.toFixed(2) + 'm' : 'Unknown'}<br>
                                    <strong>Angle:</strong> ${(det.angle * 180 / Math.PI).toFixed(1)}°<br>
                                    <strong>Position:</strong> X: ${det.bbox.xmin.toFixed(2)}, Y: ${det.bbox.ymin.toFixed(2)}
                                </div>
                            `;
                        });
                        detectionsList.innerHTML = html;
                    }
                })
                .catch(error => {
                    console.error('Error fetching detections:', error);
                });
        }
        
        // Update power data
        function updatePowerData() {
            fetch('/power_data')
                .then(response => response.json())
                .then(data => {
                    // Update temperature with color coding
                    const tempElement = document.getElementById('temperature');
                    if (data.temperature) {
                        tempElement.textContent = data.temperature.toFixed(1) + '°C';
                        tempElement.className = 'power-value ' + 
                            (data.temperature < 60 ? 'temp-good' : 
                             data.temperature < 70 ? 'temp-warning' : 'temp-danger');
                    } else {
                        tempElement.textContent = 'N/A';
                        tempElement.className = 'power-value';
                    }
                    
                    document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
                    document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
                    document.getElementById('oakd-temp').textContent = data.oakd_monitoring.chip_temp ? data.oakd_monitoring.chip_temp.toFixed(1) + '°C' : 'N/A';
                    document.getElementById('oakd-css-cpu').textContent = data.oakd_monitoring.css_cpu ? data.oakd_monitoring.css_cpu.toFixed(2) + '%' : 'N/A';
                    document.getElementById('oakd-mss-cpu').textContent = data.oakd_monitoring.mss_cpu ? data.oakd_monitoring.mss_cpu.toFixed(2) + '%' : 'N/A';
                    
                    // Display memory in MB and percentage
                    if (data.oakd_monitoring.css_memory_used && data.oakd_monitoring.css_memory_percent) {
                        const css_mb = (data.oakd_monitoring.css_memory_used / 1024 / 1024).toFixed(1);
                        document.getElementById('oakd-css-mem').textContent = css_mb + 'MB (' + data.oakd_monitoring.css_memory_percent.toFixed(1) + '%)';
                    } else {
                        document.getElementById('oakd-css-mem').textContent = 'N/A';
                    }
                    
                    if (data.oakd_monitoring.ddr_memory_used && data.oakd_monitoring.ddr_memory_percent) {
                        const ddr_mb = (data.oakd_monitoring.ddr_memory_used / 1024 / 1024).toFixed(1);
                        document.getElementById('oakd-ddr-mem').textContent = ddr_mb + 'MB (' + data.oakd_monitoring.ddr_memory_percent.toFixed(1) + '%)';
                    } else {
                        document.getElementById('oakd-ddr-mem').textContent = 'N/A';
                    }
                    
                    document.getElementById('usb-speed').textContent = data.oakd_monitoring.usb_speed || 'N/A';
                    document.getElementById('device-state').textContent = data.device_state;
                })
                .catch(error => {
                    console.error('Error fetching power data:', error);
                });
        }
        
        // Control functions
        function refreshPage() {
            location.reload();
        }
        
        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
        
        function captureImage() {
            const img = document.getElementById('camera-image');
            if (img.style.display !== 'none') {
                const link = document.createElement('a');
                link.download = 'robot_camera_' + new Date().toISOString().replace(/[:.]/g, '-') + '.png';
                link.href = img.src;
                link.click();
            }
        }
        
        function saveDetectionFrame() {
            fetch('/save_detection_frame')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Detection frame saved: ' + data.filename);
                    } else {
                        alert('Failed to save frame: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('Error saving frame: ' + error);
                });
        }
        
        function restartCamera() {
            fetch('/restart_camera')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Camera restarted successfully!');
                        location.reload();
                    } else {
                        alert('Failed to restart camera: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('Error restarting camera: ' + error);
                });
        }
        
        // Update camera status
        function updateCameraStatus() {
            fetch('/camera_status')
                .then(response => response.json())
                .then(data => {
                    const toggleBtn = document.getElementById('camera-toggle-btn');
                    const runningStatus = document.getElementById('camera-running-status');
                    
                    if (data.running) {
                        toggleBtn.textContent = '⏹️ Stop Camera';
                        toggleBtn.style.background = '#dc3545';
                        runningStatus.textContent = 'Running';
                        runningStatus.style.color = '#28a745';
                    } else {
                        toggleBtn.textContent = '📷 Start Camera';
                        toggleBtn.style.background = '#28a745';
                        runningStatus.textContent = 'Stopped';
                        runningStatus.style.color = '#dc3545';
                    }
                })
                .catch(error => {
                    console.error('Error fetching camera status:', error);
                });
        }
        
        function toggleCamera() {
            fetch('/toggle_camera')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateCameraStatus();
                        // Don't reload page, just update status
                        setTimeout(() => {
                            updateCameraStatus();
                        }, 1000);
                    } else {
                        alert('Failed to toggle camera: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('Error toggling camera: ' + error);
                });
        }
        
        // Speed slider event handler
        document.getElementById('speed-slider').addEventListener('input', function(event) {
            speedMultiplier = event.target.value / 100;
            updateMovementDisplay();
        });
        
        // Docking control functions
        function sendDockCommand() {
            const dockBtn = document.getElementById('dock-btn');
            const messageDiv = document.getElementById('dock-message');
            
            // Disable button during operation
            dockBtn.disabled = true;
            dockBtn.textContent = '🔄 Docking...';
            messageDiv.textContent = 'Sending dock command...';
            
            fetch('/dock_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.textContent = '✅ ' + data.message;
                    messageDiv.style.color = '#28a745';
                    
                    // Start monitoring dock status more frequently during docking
                    startDockMonitoring();
                } else {
                    messageDiv.textContent = '❌ ' + (data.error || data.message || 'Dock command failed');
                    messageDiv.style.color = '#dc3545';
                    
                    // Re-enable button on failure
                    dockBtn.disabled = false;
                    dockBtn.textContent = '🚀 Dock';
                }
            })
            .catch(error => {
                messageDiv.textContent = '❌ Error: ' + error.message;
                messageDiv.style.color = '#dc3545';
                
                // Re-enable button on error
                dockBtn.disabled = false;
                dockBtn.textContent = '🚀 Dock';
            });
        }
        
        function sendUndockCommand() {
            const undockBtn = document.getElementById('undock-btn');
            const messageDiv = document.getElementById('dock-message');
            
            // Disable button during operation
            undockBtn.disabled = true;
            undockBtn.textContent = '🔄 Undocking...';
            messageDiv.textContent = 'Sending undock command...';
            
            fetch('/undock_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.textContent = '✅ ' + data.message;
                    messageDiv.style.color = '#28a745';
                    
                    // Start monitoring dock status more frequently during undocking
                    startDockMonitoring();
                } else {
                    messageDiv.textContent = '❌ ' + (data.error || data.message || 'Undock command failed');
                    messageDiv.style.color = '#dc3545';
                    
                    // Re-enable button on failure
                    undockBtn.disabled = false;
                    undockBtn.textContent = '🔌 Undock';
                }
            })
            .catch(error => {
                messageDiv.textContent = '❌ Error: ' + error.message;
                messageDiv.style.color = '#dc3545';
                
                // Re-enable button on error
                undockBtn.disabled = false;
                undockBtn.textContent = '🔌 Undock';
            });
        }
        
        // Dock monitoring variables
        let dockMonitoringInterval = null;
        let dockMonitoringCount = 0;
        const MAX_DOCK_MONITORING_COUNT = 60; // Monitor for up to 60 seconds (30 checks at 2-second intervals)
        
        function startDockMonitoring() {
            // Clear any existing monitoring
            if (dockMonitoringInterval) {
                clearInterval(dockMonitoringInterval);
            }
            
            dockMonitoringCount = 0;
            
            // Check dock status every 2 seconds during docking/undocking
            dockMonitoringInterval = setInterval(() => {
                dockMonitoringCount++;
                
                fetch('/dock_status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateDockStatusDisplay(data);
                        
                        // Check if docking/undocking is complete
                        const dockBtn = document.getElementById('dock-btn');
                        const undockBtn = document.getElementById('undock-btn');
                        
                        if (data.is_docked) {
                            // Robot is docked - stop monitoring and re-enable buttons
                            stopDockMonitoring();
                            dockBtn.disabled = true;
                            undockBtn.disabled = false;
                            undockBtn.textContent = '🔌 Undock';
                            
                            const messageDiv = document.getElementById('dock-message');
                            messageDiv.textContent = '✅ Robot successfully docked!';
                            messageDiv.style.color = '#28a745';
                        } else if (!data.is_docked && dockBtn.textContent.includes('Docking')) {
                            // Robot is undocked and was previously docking - stop monitoring
                            stopDockMonitoring();
                            dockBtn.disabled = false;
                            dockBtn.textContent = '🚀 Dock';
                            undockBtn.disabled = true;
                            
                            const messageDiv = document.getElementById('dock-message');
                            messageDiv.textContent = '✅ Robot successfully undocked!';
                            messageDiv.style.color = '#28a745';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error checking dock status during monitoring:', error);
                });
                
                // Stop monitoring after maximum time
                if (dockMonitoringCount >= MAX_DOCK_MONITORING_COUNT) {
                    stopDockMonitoring();
                    
                    const dockBtn = document.getElementById('dock-btn');
                    const undockBtn = document.getElementById('undock-btn');
                    const messageDiv = document.getElementById('dock-message');
                    
                    // Re-enable buttons
                    dockBtn.disabled = false;
                    dockBtn.textContent = '🚀 Dock';
                    undockBtn.disabled = false;
                    undockBtn.textContent = '🔌 Undock';
                    
                    messageDiv.textContent = '⚠️ Dock operation timeout - please check status manually';
                    messageDiv.style.color = '#ffc107';
                }
            }, 2000);
        }
        
        function stopDockMonitoring() {
            if (dockMonitoringInterval) {
                clearInterval(dockMonitoringInterval);
                dockMonitoringInterval = null;
            }
        }
        
        function updateDockStatusDisplay(data) {
            const dockStatus = document.getElementById('dock-status');
            const seesDock = document.getElementById('sees-dock');
            
            dockStatus.textContent = data.is_docked ? '🟢 Docked' : '🔴 Undocked';
            dockStatus.style.color = data.is_docked ? '#28a745' : '#dc3545';
            
            seesDock.textContent = data.sees_dock ? '🟢 Yes' : '🔴 No';
            seesDock.style.color = data.sees_dock ? '#28a745' : '#dc3545';
        }
        
        function refreshDockStatus() {
            fetch('/dock_status')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateDockStatusDisplay(data);
                    
                    // Update button states
                    const dockBtn = document.getElementById('dock-btn');
                    const undockBtn = document.getElementById('undock-btn');
                    
                    dockBtn.disabled = data.is_docked;
                    undockBtn.disabled = !data.is_docked;
                    
                    // Update button text if not in operation
                    if (!dockBtn.textContent.includes('Docking') && !undockBtn.textContent.includes('Undocking')) {
                        dockBtn.textContent = '🚀 Dock';
                        undockBtn.textContent = '🔌 Undock';
                    }
                } else {
                    console.error('Failed to get dock status:', data.error);
                }
            })
            .catch(error => {
                console.error('Error refreshing dock status:', error);
            });
        }
        
        function updateBatteryStatusDisplay(data) {
            const batteryPercentage = document.getElementById('battery-percentage');
            const batteryVoltage = document.getElementById('battery-voltage');
            const batteryCurrent = document.getElementById('battery-current');
            const batteryCharging = document.getElementById('battery-charging');
            const batteryTemperature = document.getElementById('battery-temperature');
            const batteryStatusDiv = document.querySelector('.battery-status');
            
            // Update percentage with color coding
            const percentage = Math.round(data.percentage * 100);
            batteryPercentage.textContent = percentage;
            if (percentage <= 20) {
                batteryPercentage.style.color = '#dc3545'; // Red for low battery
            } else if (percentage <= 50) {
                batteryPercentage.style.color = '#ffc107'; // Yellow for medium battery
            } else {
                batteryPercentage.style.color = '#28a745'; // Green for good battery
            }
            
            // Update voltage
            batteryVoltage.textContent = `(${data.voltage.toFixed(1)}V)`;
            
            // Update current with color coding
            const current = data.current;
            batteryCurrent.textContent = `${current.toFixed(3)}A`;
            if (current > 0) {
                batteryCurrent.style.color = '#28a745'; // Green for charging (positive current)
            } else if (current < -1.0) {
                batteryCurrent.style.color = '#dc3545'; // Red for discharging (strong negative current)
            } else {
                batteryCurrent.style.color = '#ffc107'; // Yellow for small discharge (likely Pi consumption while charging)
            }
            
            // Update charging status with icon
            if (data.is_charging) {
                batteryCharging.textContent = '🔌 Yes';
                batteryCharging.style.color = '#28a745';
                batteryStatusDiv.classList.add('charging');
                batteryStatusDiv.classList.remove('low');
            } else {
                batteryCharging.textContent = '❌ No';
                batteryCharging.style.color = '#6c757d';
                batteryStatusDiv.classList.remove('charging');
                if (percentage <= 20) {
                    batteryStatusDiv.classList.add('low');
                } else {
                    batteryStatusDiv.classList.remove('low');
                }
            }
            
            // Update temperature
            batteryTemperature.textContent = `${data.temperature.toFixed(1)}°C`;
        }
        
        function refreshBatteryStatus() {
            fetch('/battery_status')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateBatteryStatusDisplay(data);
                } else {
                    console.error('Failed to get battery status:', data.error);
                }
            })
            .catch(error => {
                console.error('Error refreshing battery status:', error);
            });
        }
        
        // Start updates
        setInterval(updateCameraFeed, 100);
        setInterval(updateDetections, 500);
        setInterval(updatePowerData, 2000);
        setInterval(updateRobotStatus, 1000);
        setInterval(refreshDockStatus, 3000); // Refresh dock status every 3 seconds
        setInterval(refreshBatteryStatus, 2000); // Refresh battery status every 2 seconds
        
        // Initial status refresh
        refreshDockStatus();
        refreshBatteryStatus();
    </script>
</body>
</html>
"""

def create_detection_pipeline():
    """Create camera pipeline with person detection and distance measurement"""
    pipeline = dai.Pipeline()
    
    # Check for MobileNet model
    blob_paths = [
        f"{os.path.expanduser('~')}/.cache/depthai/mobilenet-ssd.blob",
        f"{os.path.expanduser('~')}/mobilenet-ssd.blob",
        "/home/irobot1/mobilenet-ssd.blob",
        "/opt/depthai-models/mobilenet-ssd.blob",
        "../mobilenet-ssd.blob",
        "mobilenet-ssd.blob"
    ]
    
    model_path = None
    for path in blob_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    if not model_path:
        print("❌ MobileNet model not found, using simple camera pipeline")
        return create_simple_pipeline()
    
    # RGB Camera
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setPreviewSize(300, 300)  # For neural network
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setFps(30)
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    
    # Depth cameras
    mono_left = pipeline.create(dai.node.MonoCamera)
    mono_right = pipeline.create(dai.node.MonoCamera)
    depth = pipeline.create(dai.node.StereoDepth)
    
    mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
    mono_left.setCamera("left")
    mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
    mono_right.setCamera("right")
    
    # Depth configuration
    depth.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)
    depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
    depth.setLeftRightCheck(True)
    depth.setSubpixel(False)
    
    # Neural network for person detection
    detection_nn = pipeline.create(dai.node.MobileNetDetectionNetwork)
    detection_nn.setConfidenceThreshold(0.3)
    detection_nn.setBlobPath(model_path)
    detection_nn.setNumInferenceThreads(2)
    detection_nn.input.setBlocking(False)
    
    # Link cameras
    mono_left.out.link(depth.left)
    mono_right.out.link(depth.right)
    cam_rgb.preview.link(detection_nn.input)
    
    # Outputs
    rgb_out = pipeline.create(dai.node.XLinkOut)
    rgb_out.setStreamName("rgb")
    cam_rgb.preview.link(rgb_out.input)
    
    depth_out = pipeline.create(dai.node.XLinkOut)
    depth_out.setStreamName("depth")
    depth.depth.link(depth_out.input)
    
    detection_out = pipeline.create(dai.node.XLinkOut)
    detection_out.setStreamName("detections")
    detection_nn.out.link(detection_out.input)
    
    return pipeline

def create_simple_pipeline():
    """Create a simple camera pipeline without neural network"""
    pipeline = dai.Pipeline()
    
    # RGB Camera
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setFps(30)
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    
    # Output
    rgb_out = pipeline.create(dai.node.XLinkOut)
    rgb_out.setStreamName("rgb")
    cam_rgb.preview.link(rgb_out.input)
    
    return pipeline

def camera_thread():
    """Camera processing thread with person detection and distance measurement"""
    global camera_frame, detection_data, camera_active, camera_error, camera_running, camera_device
    
    try:
        # Try detection pipeline first
        pipeline = create_detection_pipeline()
        camera_device = dai.Device(pipeline)
        
        # Get output queues
        q_rgb = camera_device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        q_depth = camera_device.getOutputQueue(name="depth", maxSize=4, blocking=False)
        q_det = camera_device.getOutputQueue(name="detections", maxSize=4, blocking=False)
        
        camera_active = True
        camera_error = None
        print("📷 Camera started with detection capabilities")
        
        while camera_running and camera_active:
            in_rgb = q_rgb.get()
            if in_rgb is not None:
                rgb_frame = in_rgb.getCvFrame()
                camera_frame = rgb_frame.copy()
            
                # Process detections if available
                try:
                    in_det = q_det.get()
                    if in_det is not None:
                        detections = in_det.detections
                        detected_persons = []
                        
                        for detection in detections:
                            if detection.label == 15:  # Person
                                confidence = detection.confidence
                                if confidence >= 0.3:
                                    # Calculate center point (same as robot system)
                                    center_x = int((detection.xmin + detection.xmax) * 150)
                                    center_y = int((detection.ymin + detection.ymax) * 150)
                                    
                                    # Calculate distance (same as robot system)
                                    distance = None
                                    try:
                                        in_depth = q_depth.get()
                                        if in_depth is not None:
                                            depth_frame = in_depth.getFrame()
                                            try:
                                                depth_h, depth_w = depth_frame.shape
                                                depth_x = int(center_x * depth_w / 300)
                                                depth_y = int(center_y * depth_h / 300)
                                                
                                                if 0 <= depth_x < depth_w and 0 <= depth_y < depth_h:
                                                    depth_value = depth_frame[depth_y, depth_x]
                                                    if depth_value > 0:
                                                        distance = depth_value / 1000.0  # mm to meters
                                            except Exception as e:
                                                pass
                                    except Exception as e:
                                        pass
                                    
                                    # Calculate angle (same as robot system)
                                    angle_offset = (center_x - 150) / 150.0 * 0.5
                                    
                                    person_data = {
                                        'confidence': confidence,
                                        'distance': distance,
                                        'angle': angle_offset,
                                        'bbox': {
                                            'xmin': detection.xmin,
                                            'ymin': detection.ymin,
                                            'xmax': detection.xmax,
                                            'ymax': detection.ymax
                                        }
                                    }
                                    
                                    detected_persons.append(person_data)
                                    
                                    # Draw bounding box on frame
                                    xmin = int(detection.xmin * 300)
                                    ymin = int(detection.ymin * 300)
                                    xmax = int(detection.xmax * 300)
                                    ymax = int(detection.ymax * 300)
                                    
                                    cv2.rectangle(camera_frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                                    
                                    # Add distance text
                                    distance_text = f"{distance:.2f}m" if distance else "Unknown"
                                    cv2.putText(camera_frame, f"Person: {distance_text}", 
                                              (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        detection_data = detected_persons
                except Exception as e:
                    # Detection not available, continue with just camera feed
                    pass
                
                time.sleep(0.01)
            
    except Exception as e:
        camera_error = str(e)
        camera_active = False
        print(f"❌ Camera error: {e}")
    finally:
        if 'device' in locals():
            camera_device.close()
        camera_active = False
        print("📷 Camera stopped")

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    if camera_frame is not None:
        ret, buffer = cv2.imencode('.jpg', camera_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame = buffer.tobytes()
        return Response(frame, mimetype='image/jpeg')
    else:
        return Response('', status=404)

@app.route('/detections')
def get_detections():
    """Get current detection data"""
    return jsonify({
        'camera_active': camera_active,
        'detections': detection_data,
        'error': camera_error
    })

@app.route('/power_data')
def get_power_data():
    """Get current power monitoring data"""
    power_monitor.update_power_data()
    return jsonify(power_monitor.get_power_data())

@app.route('/save_detection_frame')
def save_detection_frame():
    """Save current frame with detections"""
    try:
        if camera_frame is not None and detection_data:
            timestamp = time.strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"detected_frames/web_detection_{timestamp}.jpg"
            
            # Ensure directory exists
            os.makedirs("detected_frames", exist_ok=True)
            
            cv2.imwrite(filename, camera_frame)
            return jsonify({'success': True, 'filename': filename})
        else:
            return jsonify({'success': False, 'error': 'No frame or detections available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/restart_camera')
def restart_camera():
    """Restart camera system"""
    global camera_active
    try:
        camera_active = False
        time.sleep(1)
        camera_active = True
        threading.Thread(target=camera_thread, daemon=True).start()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/toggle_camera')
def toggle_camera():
    """Toggle camera on/off"""
    global camera_running, camera_active
    try:
        camera_running = not camera_running
        if camera_running:
            # Start camera thread if not already running
            if not camera_active:
                threading.Thread(target=camera_thread, daemon=True).start()
            return jsonify({'success': True, 'status': 'started', 'message': 'Camera started'})
        else:
            return jsonify({'success': True, 'status': 'stopped', 'message': 'Camera stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/camera_status')
def get_camera_status():
    """Get current camera status"""
    return jsonify({
        'running': camera_running,
        'active': camera_active,
        'error': camera_error
    })

@app.route('/robot_control', methods=['POST'])
def robot_control():
    """Send movement command to robot"""
    global robot_node, current_movement
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        linear_speed = data.get('linear', 0.0)
        angular_speed = data.get('angular', 0.0)
        
        # Update current movement
        current_movement['linear'] = linear_speed
        current_movement['angular'] = angular_speed
        
        # Send command to robot
        if robot_node and robot_control_active:
            success = robot_node.send_movement(linear_speed, angular_speed)
            return jsonify({'success': success})
        else:
            return jsonify({'success': False, 'error': 'Robot control not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dock_command', methods=['POST'])
def dock_command():
    """Send dock command to robot"""
    global robot_node
    
    try:
        if robot_node and robot_control_active:
            success, message = robot_node.send_dock_command()
            return jsonify({'success': success, 'message': message})
        else:
            return jsonify({'success': False, 'error': 'Robot control not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/undock_command', methods=['POST'])
def undock_command():
    """Send undock command to robot"""
    global robot_node
    
    try:
        if robot_node and robot_control_active:
            success, message = robot_node.send_undock_command()
            return jsonify({'success': success, 'message': message})
        else:
            return jsonify({'success': False, 'error': 'Robot control not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dock_status')
def get_dock_status():
    """Get current dock status"""
    global robot_node
    
    try:
        if robot_node and robot_control_active:
            status = robot_node.get_dock_status()
            return jsonify({
                'success': True,
                'is_docked': status.get('is_docked', False),
                'sees_dock': status.get('sees_dock', False)
            })
        else:
            return jsonify({'success': False, 'error': 'Robot control not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/battery_status')
def get_battery_status():
    """Get current battery status"""
    global robot_node
    
    try:
        if robot_node and robot_control_active:
            status = robot_node.get_battery_status()
            return jsonify({
                'success': True,
                'percentage': status.get('percentage', 0.0),
                'voltage': status.get('voltage', 0.0),
                'current': status.get('current', 0.0),
                'is_charging': status.get('is_charging', False),
                'power_supply_status': status.get('power_supply_status', 0),
                'temperature': status.get('temperature', 0.0)
            })
        else:
            return jsonify({'success': False, 'error': 'Robot control not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/robot_status')
def get_robot_status():
    """Get robot control status"""
    return jsonify({
        'robot_control_active': robot_control_active,
        'current_movement': current_movement,
        'ros2_available': ROS2_AVAILABLE
    })

@app.route('/stop_robot')
def stop_robot():
    """Stop robot movement"""
    global robot_node, current_movement
    
    try:
        if robot_node and robot_control_active:
            success = robot_node.stop_robot()
            current_movement = {'linear': 0.0, 'angular': 0.0}
            return jsonify({'success': success})
        else:
            return jsonify({'success': False, 'error': 'Robot control not available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def power_monitoring_thread():
    """Background thread for power monitoring"""
    while True:
        try:
            power_monitor.update_power_data()
            time.sleep(2)  # Update every 2 seconds
        except Exception as e:
            print(f"Power monitoring error: {e}")
            time.sleep(5)

def main():
    """Main function"""
    print("🌐 Starting Web Camera Viewer with Distance Detection & Robot Control")
    print("=" * 60)
    print("📷 Initializing camera system...")
    
    # Initialize robot control
    print("🤖 Initializing robot control...")
    if init_robot_control():
        print("✅ Robot control initialized")
    else:
        print("⚠️  Robot control not available - continuing without robot control")
    
    # Start camera thread
    threading.Thread(target=camera_thread, daemon=True).start()
    
    # Start power monitoring thread
    threading.Thread(target=power_monitoring_thread, daemon=True).start()
        
    # Start Flask app
    print("🌐 Starting web server...")
    print("📱 Access the viewer at: http://localhost:5000")
    print("🌍 Or from other devices: http://[PI_IP]:5000")
    print("🎮 Use arrow keys to control the robot (if available)")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
    finally:
        # Cleanup
        global robot_node, camera_running
        camera_running = False
        
        # Stop robot
        if robot_node:
            try:
                robot_node.stop_robot()
                print("🤖 Robot stopped")
            except:
                pass
        
        # Shutdown ROS2
        if ROS2_AVAILABLE and rclpy.ok():
            try:
                rclpy.shutdown()
                print("🔄 ROS2 shutdown complete")
            except:
                pass
        
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()