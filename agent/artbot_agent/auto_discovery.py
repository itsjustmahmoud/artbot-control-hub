import os
import subprocess
import socket
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AutoDiscovery:
    """Auto-discovers robot and system information"""
    
    def __init__(self, config):
        self.config = config
    
    async def detect_robot_info(self):
        """Detect robot information and capabilities"""
        robot_info = {
            "type": "unknown",
            "model": "unknown",
            "capabilities": [],
            "sensors": [],
            "ros2_available": False,
            "person_following_available": False
        }
        
        try:
            # Check if this is a Raspberry Pi
            if self.is_raspberry_pi():
                robot_info["type"] = "raspberry_pi"
                robot_info["model"] = self.get_pi_model()
            
            # Check if ROS2 is available
            if self.check_ros2_available():
                robot_info["ros2_available"] = True
                robot_info["capabilities"].append("ros2")
                
                # Check for person following system
                if self.check_person_following_available():
                    robot_info["person_following_available"] = True
                    robot_info["capabilities"].append("person_following")
            
            # Check for sensors
            sensors = self.detect_sensors()
            robot_info["sensors"] = sensors
            
            # Check for Create3 robot
            if self.check_create3_available():
                robot_info["type"] = "irobot_create3"
                robot_info["capabilities"].append("create3")
            
            # Check for OAK camera
            if self.check_oak_camera():
                robot_info["sensors"].append("oak_camera")
                robot_info["capabilities"].append("depth_perception")
            
            logger.info(f"Detected robot info: {robot_info}")
            
        except Exception as e:
            logger.error(f"Error during robot detection: {e}")
        
        return robot_info
    
    def is_raspberry_pi(self):
        """Check if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def get_pi_model(self):
        """Get Raspberry Pi model"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().strip('\x00')
                return model
        except:
            return "unknown"
    
    def check_ros2_available(self):
        """Check if ROS2 is installed and available"""
        try:
            # Check if ROS2 workspace exists
            if os.path.exists(self.config.ros2_workspace):
                return True
            
            # Check if ros2 command is available
            result = subprocess.run(
                ["which", "ros2"],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error checking ROS2: {e}")
            return False
    
    def check_person_following_available(self):
        """Check if person following package is available"""
        try:
            package_path = os.path.join(
                self.config.ros2_workspace,
                "src",
                self.config.ros2_package
            )
            
            return os.path.exists(package_path)
            
        except Exception as e:
            logger.error(f"Error checking person following package: {e}")
            return False
    
    def detect_sensors(self):
        """Detect available sensors"""
        sensors = []
        
        try:
            # Check for cameras
            if self.check_cameras():
                sensors.append("camera")
            
            # Check for USB devices (might include sensors)
            usb_devices = self.get_usb_devices()
            
            # Look for known sensor patterns
            for device in usb_devices:
                if "realsense" in device.lower():
                    sensors.append("realsense")
                elif "oak" in device.lower() or "luxonis" in device.lower():
                    sensors.append("oak_camera")
                elif "lidar" in device.lower():
                    sensors.append("lidar")
            
        except Exception as e:
            logger.error(f"Error detecting sensors: {e}")
        
        return sensors
    
    def check_cameras(self):
        """Check for available cameras"""
        try:
            # Check for video devices
            video_devices = []
            for i in range(10):  # Check first 10 video devices
                device_path = f"/dev/video{i}"
                if os.path.exists(device_path):
                    video_devices.append(device_path)
            
            return len(video_devices) > 0
            
        except Exception as e:
            logger.error(f"Error checking cameras: {e}")
            return False
    
    def get_usb_devices(self):
        """Get list of USB devices"""
        try:
            result = subprocess.run(
                ["lsusb"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.split('\n')
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting USB devices: {e}")
            return []
    
    def check_create3_available(self):
        """Check if Create3 robot is connected"""
        try:
            # Check for Create3 specific indicators
            # This would depend on how Create3 is connected (USB, network, etc.)
            
            # Check if Create3 ROS2 packages are available
            create3_indicators = [
                "irobot_create_msgs",
                "create3_examples"
            ]
            
            for indicator in create3_indicators:
                # Simple check - could be more sophisticated
                if indicator in str(subprocess.run(["find", "/", "-name", f"*{indicator}*"], 
                                                 capture_output=True, text=True).stdout):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking Create3: {e}")
            return False
    
    def check_oak_camera(self):
        """Check for OAK (OpenCV AI Kit) camera"""
        try:
            # Check for OAK-specific USB devices
            usb_devices = self.get_usb_devices()
            
            for device in usb_devices:
                if "03e7" in device:  # Luxonis vendor ID
                    return True
            
            # Check for DepthAI installation
            try:
                import depthai
                return True
            except ImportError:
                pass
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking OAK camera: {e}")
            return False
    
    def get_network_info(self):
        """Get network configuration"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            return {
                "hostname": hostname,
                "ip_address": ip_address,
                "interfaces": self.get_network_interfaces()
            }
            
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {"hostname": "unknown", "ip_address": "unknown", "interfaces": []}
    
    def get_network_interfaces(self):
        """Get network interface information"""
        try:
            result = subprocess.run(
                ["ip", "addr", "show"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse interface information (simplified)
                lines = result.stdout.split('\n')
                interfaces = []
                
                for line in lines:
                    if line.startswith(' ') and 'inet ' in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            interfaces.append(parts[1])
                
                return interfaces
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting network interfaces: {e}")
            return []
