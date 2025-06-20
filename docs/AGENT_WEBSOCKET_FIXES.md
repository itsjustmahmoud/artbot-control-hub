# Agent WebSocket Connection Issues - Analysis & Fixes

## Problem Analysis

Based on the logs you provided, the agent was shutting down immediately after the WebSocket connection was closed by the server. Here are the root causes identified:

### 1. **No Reconnection Logic**
- **Issue**: Agent exited completely when WebSocket connection closed
- **Cause**: No retry mechanism in the main loop
- **Impact**: Any temporary network issue or server restart would kill the agent

### 2. **Missing WebSocket Communication**
- **Issue**: Agent wasn't sending required messages via WebSocket
- **Cause**: Only HTTP heartbeats were implemented, not WebSocket heartbeats
- **Impact**: Server closed connection due to inactivity

### 3. **Incomplete Message Protocol**
- **Issue**: Backend expected specific message types from agents
- **Expected**: `heartbeat`, `robot_status`, `command_response`
- **Agent was sending**: Only command responses

## Fixes Implemented

### ✅ 1. Added WebSocket Reconnection Logic
```python
# Main loop with reconnection
while self.running:
    try:
        # Connect WebSocket
        if not await self.connect_websocket():
            logger.error("Failed to establish WebSocket connection, retrying in 10 seconds...")
            await asyncio.sleep(10)
            continue
        
        # Handle messages
        await self.handle_websocket_messages()
        
    except Exception as e:
        logger.error(f"Agent error: {e}")
    finally:
        # Cleanup and retry if still running
        if self.running:
            logger.info("WebSocket disconnected, reconnecting in 5 seconds...")
            await asyncio.sleep(5)
```

### ✅ 2. Added WebSocket Heartbeat Messages
```python
async def websocket_heartbeat_loop(self):
    """Send periodic heartbeat via WebSocket"""
    while self.running:
        essential_metrics = await self.system_monitor.get_essential_metrics()
        await self.send_websocket_message("heartbeat", essential_metrics)
        await asyncio.sleep(self.config.heartbeat_interval)
```

### ✅ 3. Added WebSocket Status Updates
```python
async def websocket_status_loop(self):
    """Send periodic status updates via WebSocket"""
    while self.running:
        robot_status = await self.system_monitor.get_essential_metrics()
        await self.send_websocket_message("robot_status", robot_status)
        await asyncio.sleep(self.config.monitor_interval)
```

### ✅ 4. Added Proper Message Sending
```python
async def send_websocket_message(self, message_type: str, data: dict):
    """Send message via WebSocket"""
    message = {
        "type": message_type,
        "agent_id": self.config.agent_id,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    await self.websocket.send(json.dumps(message))
```

## Expected Behavior After Fix

### 🔄 **Automatic Reconnection**
- Agent will automatically reconnect if WebSocket connection drops
- Retries every 5-10 seconds indefinitely
- No more immediate shutdowns on connection loss

### 💓 **Active Communication**
- Sends heartbeat every 30 seconds (configurable)
- Sends robot status every 10 seconds (configurable)  
- Server won't close connection due to inactivity

### 🚀 **Robust Operation**
- Handles network interruptions gracefully
- Maintains connection state properly
- Provides better logging for debugging

## Testing the Fixes

### 1. **Deploy Updated Agent**
```bash
# On your Pi, update the agent code
cd ~/artbot-control-hub
git pull origin main

# Restart the agent
python3 -m artbot_agent.main
```

### 2. **Check Logs for Expected Behavior**
```bash
# You should see these patterns:
INFO:__main__:WebSocket connection established
INFO:__main__:Background tasks started
DEBUG:__main__:Sent heartbeat message via WebSocket
DEBUG:__main__:Sent robot_status message via WebSocket

# If connection drops, you should see:
WARNING:__main__:WebSocket connection closed by server  
INFO:__main__:WebSocket disconnected, reconnecting in 5 seconds...
INFO:__main__:Connecting to WebSocket (attempt 1/5)
INFO:__main__:WebSocket connection established
```

### 3. **Test Connection Resilience**
```bash
# Test 1: Restart backend server while agent is running
# Agent should reconnect automatically

# Test 2: Simulate network interruption
sudo iptables -A OUTPUT -p tcp --dport 8000 -j DROP
# Wait 10 seconds
sudo iptables -D OUTPUT -p tcp --dport 8000 -j DROP
# Agent should reconnect
```

## Backend Compatibility

The backend already supports these message types:
- ✅ `heartbeat` → Updates agent heartbeat
- ✅ `robot_status` → Updates robot status and broadcasts to dashboard
- ✅ `command_response` → Handles command responses

No backend changes needed!

## Configuration Options

You can adjust timing in the agent's `.env` file:
```bash
HEARTBEAT_INTERVAL=30     # Heartbeat every 30 seconds
MONITOR_INTERVAL=10       # Status updates every 10 seconds
```

## Why This Fixes the Issue

1. **Server keeps connection alive** because it receives regular messages
2. **Network issues are handled** with automatic reconnection
3. **No single point of failure** - temporary issues don't kill the agent
4. **Better monitoring** - hub gets real-time status updates

The agent should now stay connected reliably and provide continuous monitoring data to your dashboard!
