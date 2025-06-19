# API Documentation

## Authentication

All API endpoints (except `/auth/validate`) require authentication using JWT Bearer tokens.

### Authentication Endpoints

#### POST /api/auth/validate
Validate password and get access token.

**Request:**
```json
{
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "access_level": "ADMIN|MUSEUM", 
  "expires_in": 28800
}
```

### Headers
```
Authorization: Bearer <jwt-token>
```

## Robot Control

### GET /api/robots
Get all robots with their status.

**Response:**
```json
{
  "robots": [
    {
      "id": "robot-001",
      "status": "active|idle|offline|restarting",
      "current_action": "person_following|stopped|system_restart",
      "battery_level": 85,
      "last_update": "2024-01-01T12:00:00Z",
      "agent_id": "robot-001"
    }
  ],
  "total": 2,
  "online": 1
}
```

### GET /api/robots/{robot_id}
Get specific robot information.

### POST /api/robots/{robot_id}/command
Send command to robot.

**Request:**
```json
{
  "action": "start|stop|restart|reboot",
  "parameters": {}
}
```

### POST /api/robots/exhibition/command
Control entire exhibition.

**Request:**
```json
{
  "action": "start_all|stop_all"
}
```

### GET /api/robots/exhibition/status
Get exhibition status.

**Response:**
```json
{
  "total_robots": 2,
  "online_robots": 2,
  "active_robots": 1,
  "exhibition_running": true,
  "last_update": "2024-01-01T12:00:00Z"
}
```

## Agent Management

### POST /api/agents/register
Register new agent (called by Pi agents).

**Request:**
```json
{
  "agent_id": "robot-001",
  "hostname": "robot-001",
  "ip_address": "192.168.1.100",
  "system_info": {
    "platform": "Linux-5.4.0-rpi",
    "python_version": "3.9.2"
  },
  "robot_info": {
    "type": "irobot_create3",
    "capabilities": ["ros2", "person_following"]
  }
}
```

### POST /api/agents/{agent_id}/heartbeat
Agent heartbeat endpoint.

### GET /api/agents
Get all agents (Admin only).

## System Monitoring

### GET /api/system/health
Get system health status.

### GET /api/system/status
Get system status summary.

## Logs

### GET /api/logs
Get system logs with filtering.

**Query Parameters:**
- `limit`: Number of logs to return (default: 100)
- `level`: Filter by log level
- `robot_id`: Filter by robot ID

## WebSocket Endpoints

### /ws/robots
Real-time robot updates.

### /ws/logs
Real-time log streaming.

### /ws/agent/{agent_id}
Agent communication channel.

## Permission Levels

### ADMIN
- Full system access
- All robot operations
- Agent management
- System configuration

### MUSEUM
- View robot status
- Start/stop exhibition
- Basic log viewing
- Read-only monitoring

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

HTTP Status Codes:
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error
