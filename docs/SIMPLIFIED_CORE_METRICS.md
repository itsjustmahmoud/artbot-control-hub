# Updated Core Metrics Requirements

## Simplified Required Data Points

Based on your feedback, here are the **simplified required data points** for the Artbot Control Hub:

### 🖥️ **System Metrics**
1. **CPU Usage** (`cpu_percent`) - Pi CPU utilization percentage
2. **Temperature** (`temperature`) - Pi system temperature in Celsius  
3. **Memory Usage** (`memory_percent`) - Pi RAM usage percentage

### 📷 **OAK-D Camera** 
4. **OAK-D Connected** (`oak_connected`) - **Boolean connection status only** ✅

### 🤖 **Create3 Robot**
5. **Create3 Connected** (`create3_connected`) - Boolean ROS2 connection status
6. **Create3 Status** (`create3_status`) - Robot operational state
7. **Battery Level** (`battery_level`) - Battery percentage (0-100)
8. **Is Charging** (`is_charging`) - Boolean charging status
9. **Is Docked** (`is_docked`) - Boolean docking status

### 🔧 **Workspace & Agent**
10. **Workspace Running** (`workspace_running`) - Boolean if workspace run is active
11. **Agent Uptime** (`uptime`) - Seconds since agent started
12. **Hostname** - Pi hostname/identifier
13. **Agent ID** - Unique agent identifier

## What Changed

### ❌ **Removed: Detailed OAK-D Data**
- No more `oakd_data` object with detailed camera information
- No more chip temperature, CPU usage, memory usage from camera
- No more USB speed, device name, MXID
- No more device state or error details

### ✅ **Kept: Simple Connection Status**
- Only `oak_connected: true/false` 
- Still uses non-intrusive monitoring (doesn't block other camera apps)
- Still detects camera presence via USB/sysfs checks

## Updated API Response

```json
{
  "robot_id": "artbot1_robot",
  "hostname": "artbot1",
  "agent_id": "artbot1_robot", 
  "timestamp": "2025-06-20T10:30:00Z",
  
  // System Metrics
  "cpu_percent": 25.4,
  "temperature": 42.1,
  "memory_percent": 68.2,
  
  // OAK-D Camera (simplified)
  "oak_connected": true,
  
  // Create3 Robot
  "create3_connected": true,
  "create3_status": "docked",
  "battery_level": 85.3,
  "is_charging": true,
  "is_docked": true,
  
  // Workspace & Agent
  "workspace_running": false,
  "uptime": 3600
}
```

## Benefits of Simplification

✅ **Faster response times** - Less data to collect and transmit  
✅ **Reduced complexity** - Simpler agent code and API responses  
✅ **Better reliability** - Fewer potential points of failure  
✅ **Still non-intrusive** - Camera remains available for other applications  
✅ **Focus on essentials** - Only critical connectivity information  

## Total Data Points: 13

This gives you all the essential monitoring information while keeping the OAK-D monitoring simple and reliable. The agent will still detect if the camera is connected, but won't collect detailed internal metrics unless explicitly needed in the future.
