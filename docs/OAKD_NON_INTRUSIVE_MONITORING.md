# OAK-D Non-Intrusive Monitoring

## Overview

The Artbot Control Hub now uses **non-intrusive monitoring** for OAK-D cameras by default. This means:

✅ **Camera connectivity is detected** without opening the device
✅ **Other applications can use the camera** simultaneously  
✅ **No exclusive locks** on the camera hardware
✅ **Basic device info** is still collected

## What Changed

### Before (Intrusive Mode)
- Agent opened OAK-D device with `depthai.Device()`
- Camera became unavailable to other scripts
- Detailed internal metrics were collected
- Camera was held open continuously

### Now (Non-Intrusive Mode - Default)
- Agent detects camera via `lsusb` and sysfs checks
- Camera remains available for other applications
- Basic device info collected without opening device
- No exclusive hardware access

## Available Monitoring Modes

### 1. Non-Intrusive Mode (Default)
```python
# Automatically used by default
status = await get_oakd_status()
print(f"Connected: {status['connected']}")  # True if detected via USB
```

**Provides:**
- Device connectivity status
- USB device type detection
- Basic device presence
- No interference with other camera apps

### 2. Intrusive Mode (Optional)
```python
# Only use when detailed metrics are specifically needed
from artbot_agent.oakd_monitor import oakd_monitor

# Enable detailed monitoring (opens device)
oakd_monitor.enable_intrusive_monitoring()

# Disable and free the device
oakd_monitor.disable_intrusive_monitoring()
```

**Provides:**
- All non-intrusive data PLUS:
- Chip temperature
- CPU usage (CSS/MSS)
- Memory usage (CSS/DDR)
- USB speed
- Device MXID
- Internal performance metrics

## API Response Changes

### Non-Intrusive Response
```json
{
  "oakd_data": {
    "connected": true,
    "device_state": "Inactive", 
    "device_type": "OAK-D Lite",
    "device_name": "OAK-D Lite",
    "error": "Non-intrusive mode - device detected but not opened",
    "chip_temperature": null,
    "css_cpu_usage": null,
    "mss_cpu_usage": null,
    "css_memory_percent": null,
    "ddr_memory_percent": null,
    "usb_speed": null,
    "mxid": null
  }
}
```

### Intrusive Response (when enabled)
```json
{
  "oakd_data": {
    "connected": true,
    "device_state": "Active",
    "device_type": "OAK-D Lite", 
    "device_name": "OAK-D",
    "error": null,
    "chip_temperature": 45.2,
    "css_cpu_usage": 12.5,
    "mss_cpu_usage": 8.3,
    "css_memory_percent": 15.7,
    "ddr_memory_percent": 22.1,
    "usb_speed": "SUPER",
    "mxid": "18443010D1A0261200"
  }
}
```

## Testing

Run the non-intrusive monitoring test:

```bash
cd /path/to/artbot-control-hub
python test_oakd_non_intrusive.py
```

This will verify:
- ✅ OAK-D is detected without opening device
- ✅ Camera remains available for other scripts
- ✅ Monitoring provides correct connectivity status

## Benefits

1. **No Camera Blocking**: Other vision applications can run simultaneously
2. **Faster Startup**: No device initialization delays
3. **Lower Resource Usage**: No continuous device polling
4. **Better Reliability**: Eliminates device access conflicts
5. **Flexible Monitoring**: Can enable detailed metrics only when needed

## Migration Notes

### For Existing Code
- `oak_connected` still works as expected
- Basic OAK-D status is still available in metrics API
- No changes needed for standard monitoring use cases

### For Advanced Monitoring
- If you need detailed OAK-D metrics, explicitly enable intrusive mode
- Remember to disable intrusive mode when done to free the camera
- Consider using intrusive mode only during debugging/diagnostics

## Troubleshooting

### Camera Not Detected
```bash
# Check USB devices
lsusb | grep "03e7:2485"

# Check agent logs
tail -f /path/to/agent.log | grep -i oak
```

### Still Can't Access Camera
```bash
# Ensure intrusive monitoring is disabled
curl -X GET http://localhost:8000/api/robots/your-robot-id/metrics
# Look for "Non-intrusive mode" in oakd_data.error
```

### Need Detailed Metrics
```python
# Temporarily enable intrusive monitoring
from artbot_agent.oakd_monitor import oakd_monitor
oakd_monitor.enable_intrusive_monitoring()

# Get detailed metrics
status = await get_oakd_status()

# Don't forget to disable
oakd_monitor.disable_intrusive_monitoring()
```
