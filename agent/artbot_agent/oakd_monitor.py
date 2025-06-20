#!/usr/bin/env python3
"""
OAK-D Camera Monitor Module
Comprehensive monitoring of OAK-D camera device based on reference implementation
Monitors power consumption, internal metrics, and device status
"""

import os
import subprocess
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# Try to import depthai for OAK-D monitoring
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False
    logger.warning("depthai not available - OAK-D internal monitoring disabled")

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - system monitoring disabled")


class OAKDMonitor:
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
                'css_memory_used': None,
                'css_memory_total': None,
                'css_memory_percent': None,
                'ddr_memory_used': None,
                'ddr_memory_total': None,
                'ddr_memory_percent': None,
                'usb_speed': None,
                'device_name': None,
                'mxid': None,
                'error': None
            },
            'device_state': 'Unknown',
            'device_info': None,
            'last_update': None,
            'connected': False
        }
        self.camera_device = None
        self.camera_active = False
    
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
            logger.debug(f"Device info error: {e}")
        return None
    
    def get_device_temperature(self):
        """Get system temperature (Raspberry Pi)"""
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
    
    def get_oakd_monitoring(self, enable_intrusive_monitoring=False):
        """Get OAK-D internal monitoring data
        
        Args:
            enable_intrusive_monitoring: If True, opens the device for detailed metrics.
                                       If False (default), returns basic device info only.
        """
        # Basic device detection without opening the device
        basic_data = {
            'chip_temp': None,
            'css_cpu': None,
            'mss_cpu': None,
            'css_memory_used': None,
            'css_memory_total': None,
            'css_memory_percent': None,
            'ddr_memory_used': None,
            'ddr_memory_total': None,
            'ddr_memory_percent': None,
            'usb_speed': None,
            'device_name': None,
            'mxid': None,
            'error': None
        }
        
        # If intrusive monitoring is disabled, return basic data only
        if not enable_intrusive_monitoring:
            # Just check if device is present via lsusb without opening it
            try:
                oakd_check = subprocess.run(
                    "lsusb | grep '03e7:2485'", 
                    shell=True, capture_output=True, text=True
                )
                if oakd_check.returncode == 0:
                    basic_data['device_name'] = 'OAK-D Lite'
                    basic_data['error'] = 'Non-intrusive mode - device detected but not opened'
                else:
                    basic_data['error'] = 'Device not found via lsusb'
            except Exception as e:
                basic_data['error'] = f'Detection error: {str(e)}'
            
            return basic_data
        
        # Intrusive monitoring - only if explicitly enabled
        if not DEPTHAI_AVAILABLE:
            basic_data['error'] = 'depthai not available'
            return basic_data
        
        try:
            # Use existing camera device if available, otherwise create new one
            device = None
            if self.camera_device and self.camera_active:
                device = self.camera_device
            else:
                try:
                    device = dai.Device()
                    logger.info("OAK-D device opened for intrusive monitoring")
                except Exception as e:
                    basic_data['error'] = f'Device not available: {str(e)}'
                    return basic_data
            
            if not device:
                basic_data['error'] = 'Could not access device'
                return basic_data
            
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
            
            # Store device reference if we created a new one
            if not self.camera_device:
                self.camera_device = device
            
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
            basic_data['error'] = str(e)
            return basic_data
    
    def update_power_data(self):
        """Update power monitoring data"""
        # Update system metrics if psutil is available
        if PSUTIL_AVAILABLE:
            self.power_data['cpu_usage'] = psutil.cpu_percent(interval=1)
            self.power_data['memory_usage'] = psutil.virtual_memory().percent
        else:
            self.power_data['cpu_usage'] = 0.0
            self.power_data['memory_usage'] = 0.0
          # Update OAK-D specific data - use non-intrusive monitoring by default
        self.power_data['usb_power_info'] = self.get_usb_power()
        self.power_data['oakd_monitoring'] = self.get_oakd_monitoring(enable_intrusive_monitoring=False)
        self.power_data['temperature'] = self.get_device_temperature()
        self.power_data['device_state'] = 'Active' if self.camera_active else 'Inactive'
        self.power_data['device_info'] = self.get_device_info()
        self.power_data['last_update'] = time.strftime('%H:%M:%S')
        
        # Determine if OAK-D is connected - check USB presence
        usb_info = self.power_data['usb_power_info']
        
        self.power_data['connected'] = (
            usb_info.get('status') != 'OAK-D Not Found' and
            usb_info.get('status') != 'Error'
        )
    
    def get_power_data(self):
        """Get current power data"""
        return self.power_data
    
    def set_camera_active(self, active: bool):
        """Set camera active state"""
        self.camera_active = active
    
    def set_camera_device(self, device):
        """Set camera device reference"""
        self.camera_device = device
    
    def is_connected(self):
        """Check if OAK-D is connected"""
        return self.power_data.get('connected', False)
    
    def get_status_summary(self):
        """Get a summary of OAK-D status for agent reporting"""
        self.update_power_data()
        
        oakd_data = self.power_data['oakd_monitoring']
        usb_data = self.power_data['usb_power_info']
        
        return {
            'connected': self.power_data['connected'],
            'device_state': self.power_data['device_state'],
            'device_type': usb_data.get('device_type', 'Unknown'),
            'chip_temperature': oakd_data.get('chip_temp'),
            'css_cpu_usage': oakd_data.get('css_cpu'),
            'mss_cpu_usage': oakd_data.get('mss_cpu'),
            'css_memory_percent': oakd_data.get('css_memory_percent'),
            'ddr_memory_percent': oakd_data.get('ddr_memory_percent'),
            'usb_speed': oakd_data.get('usb_speed'),
            'device_name': oakd_data.get('device_name'),
            'mxid': oakd_data.get('mxid'),
            'last_update': self.power_data['last_update'],
            'error': oakd_data.get('error')
        }
    
    def enable_intrusive_monitoring(self):
        """Enable intrusive OAK-D monitoring for detailed metrics
        
        This will open the device and get detailed internal metrics.
        Only use when detailed OAK-D metrics are specifically needed.
        """
        try:
            self.power_data['oakd_monitoring'] = self.get_oakd_monitoring(enable_intrusive_monitoring=True)
            logger.info("Intrusive OAK-D monitoring enabled")
            return True
        except Exception as e:
            logger.error(f"Failed to enable intrusive OAK-D monitoring: {e}")
            return False
    
    def disable_intrusive_monitoring(self):
        """Disable intrusive monitoring and close device if needed"""
        try:
            if self.camera_device:
                # Close the device to free it for other applications
                self.camera_device.close()
                self.camera_device = None
                logger.info("OAK-D device closed - available for other applications")
            
            # Switch back to non-intrusive monitoring
            self.power_data['oakd_monitoring'] = self.get_oakd_monitoring(enable_intrusive_monitoring=False)
            return True
        except Exception as e:
            logger.error(f"Error disabling intrusive monitoring: {e}")
            return False

# Global instance for the agent to use
oakd_monitor = OAKDMonitor()


async def get_oakd_status():
    """Async wrapper to get OAK-D status"""
    try:
        return oakd_monitor.get_status_summary()
    except Exception as e:
        logger.error(f"Error getting OAK-D status: {e}")
        return {
            'connected': False,
            'device_state': 'Error',
            'error': str(e)
        }


def initialize_oakd_monitoring():
    """Initialize OAK-D monitoring"""
    logger.info("Initializing OAK-D monitoring...")
    try:
        oakd_monitor.update_power_data()
        logger.info("✅ OAK-D monitoring initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize OAK-D monitoring: {e}")
        return False


def update_oakd_camera_state(active: bool, device=None):
    """Update OAK-D camera state"""
    oakd_monitor.set_camera_active(active)
    if device:
        oakd_monitor.set_camera_device(device)
