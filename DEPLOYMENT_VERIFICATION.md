# LightBox Production Deployment Verification

**Document Version**: 1.0  
**Last Updated**: 2025-06-23  
**Production URL**: http://192.168.0.222:5001  
**System**: Raspberry Pi with WS2811/NeoPixel LED Matrix

## Pre-Deployment Checklist

### ✅ **System Requirements**
- [ ] Raspberry Pi 4 or Pi Zero W with Raspberry Pi OS
- [ ] Python 3.11+ installed and verified
- [ ] User added to gpio group: `sudo usermod -a -G gpio $USER`
- [ ] Virtual environment created in `LightBox/venv/`
- [ ] All dependencies installed via `pip install -r requirements.txt`

### ✅ **Hardware Setup**
- [ ] WS2811/NeoPixel LED matrix connected to GPIO18 (pin 12)
- [ ] Power supply adequate for LED count (5V, sufficient amperage)
- [ ] GPIO access verified: `/dev/gpiomem` or `/dev/mem` accessible
- [ ] Hardware test passed: `python3 LightBox/scripts/matrix_test.py`

### ✅ **Software Configuration**
- [ ] Settings.json configured with correct matrix dimensions
- [ ] Web port configured (default 5001, avoid conflicts)
- [ ] All animation scripts validated for color range compliance
- [ ] Service configuration updated with correct paths

## Deployment Process

### Step 1: Pre-Deployment Tests

```bash
cd ~/LightBox
source venv/bin/activate

# Test 1: Animation validation
python3 animation_test.py

# Test 2: Hardware production test (requires sudo)
sudo python3 production_test.py

# Test 3: Web interface test
python3 -c "from webgui.app import create_app; from config import Config; app = create_app(None, Config()); print('Web app imports OK')"
```

**Expected Results**:
- ✅ All animations pass color range validation
- ✅ Hardware test shows successful LED control
- ✅ Web interface imports without errors

### Step 2: Service Installation

```bash
# Install and configure systemd service
sudo python3 service_manager.py install

# Verify service file
sudo systemctl cat lightbox

# Start service
sudo python3 service_manager.py start
```

**Expected Results**:
- ✅ Service installed successfully
- ✅ Service starts without errors
- ✅ No permission errors in logs

### Step 3: Production Verification

#### A. Service Status Check
```bash
# Check service status
python3 service_manager.py status

# Check logs
python3 service_manager.py logs 20
```

**Expected Results**:
- ✅ Service status: `active (running)`
- ✅ No error messages in recent logs
- ✅ Animation loop starting messages visible

#### B. Hardware Functionality
```bash
# Test with actual hardware (service must be stopped first)
sudo python3 service_manager.py stop
sudo python3 production_test.py
sudo python3 service_manager.py start
```

**Expected Results**:
- ✅ LED matrix displays test patterns
- ✅ No "byte must be in range" errors
- ✅ Smooth animation transitions

#### C. Web Interface Verification

**Health Check Endpoint**:
```bash
curl -s http://192.168.0.222:5001/api/health | python3 -m json.tool
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-23T...",
  "uptime_seconds": 120.5,
  "matrix": {
    "running": true,
    "has_frames": true,
    "current_program": "cosmic",
    "frame_count": 3000,
    "fps": 30
  },
  "system": {
    "memory_percent": 45.2,
    "cpu_percent": 25.1,
    "gpio_available": true,
    "error_count": 0
  }
}
```

**Status Endpoint**:
```bash
curl -s http://192.168.0.222:5001/api/status | python3 -m json.tool
```

**Expected Response**:
```json
{
  "running": true,
  "current_program": "cosmic",
  "fps": 30,
  "frame_count": 3000,
  "uptime_formatted": "2 minutes",
  "programs": [...],
  "config": {...}
}
```

**Web Interface Access**:
- [ ] Navigate to http://192.168.0.222:5001
- [ ] Verify main interface loads
- [ ] Test animation switching
- [ ] Test brightness controls
- [ ] Test color palette changes

## Performance Validation

### Resource Usage Limits
- **Memory**: < 512MB (systemd limit)
- **CPU**: < 80% sustained (systemd limit)
- **FPS**: 30fps on Pi 4, 15fps on Pi Zero W
- **Response Time**: API responses < 500ms

### Performance Test
```bash
# Monitor resource usage
top -p $(pgrep -f CosmicLED.py)

# Monitor logs for performance data
tail -f logs/performance.log
```

**Expected Performance**:
- ✅ Memory usage stable under 400MB
- ✅ CPU usage under 60% during normal operation
- ✅ Consistent FPS within 5% of target
- ✅ No memory leaks over 24-hour operation

## Error Handling Verification

### Test Error Recovery
```bash
# Test invalid animation program
curl -X POST http://192.168.0.222:5001/api/program \
  -H "Content-Type: application/json" \
  -d '{"program": "nonexistent"}'

# Check system recovery
curl -s http://192.168.0.222:5001/api/health
```

**Expected Behavior**:
- ✅ System returns to safe built-in animation
- ✅ Error logged but system continues running
- ✅ Health check still reports healthy status

### Test Service Recovery
```bash
# Simulate crash
sudo pkill -9 -f CosmicLED.py

# Wait for systemd restart (10 seconds)
sleep 15

# Verify recovery
python3 service_manager.py status
```

**Expected Behavior**:
- ✅ Service automatically restarts
- ✅ Animation resumes within 15 seconds
- ✅ No permanent LED artifacts

## Security Validation

### Service Security
- [ ] Service runs as root (required for GPIO access)
- [ ] Temporary files isolated (`PrivateTmp=true`)
- [ ] Device access limited to GPIO devices only
- [ ] No unnecessary privileges escalated

### Web Interface Security
- [ ] CORS headers configured appropriately
- [ ] File upload validation working
- [ ] No sensitive information exposed in API responses
- [ ] Rate limiting functional (if implemented)

## Troubleshooting Guide

### Common Issues

#### Issue: "NeoPixel support requires running with sudo"
**Symptoms**: Animation starts but no LED output
**Solution**: Ensure service runs as root user
```bash
sudo systemctl edit lightbox --full
# Verify: User=root, Group=root
```

#### Issue: "byte must be in range(0, 256)"
**Symptoms**: Repeated error messages, animation crashes
**Solution**: Animation color validation issue
```bash
# Test specific animation
python3 animation_test.py [animation_name]
# Fix color calculations in problematic animations
```

#### Issue: High CPU usage
**Symptoms**: System sluggish, >90% CPU
**Solution**: Check FPS settings and animation complexity
```bash
# Reduce FPS temporarily
curl -X POST http://192.168.0.222:5001/api/config \
  -H "Content-Type: application/json" \
  -d '{"fps": 15}'
```

#### Issue: Web interface not accessible
**Symptoms**: Connection refused on port 5001
**Solution**: Check port conflicts and firewall
```bash
# Check if port is in use
sudo netstat -tlnp | grep 5001
# Check service logs
python3 service_manager.py logs 50
```

### Log Analysis

**Key Log Files**:
- `logs/lightbox.log` - Main application logs
- `logs/animation.log` - Animation-specific logs
- `logs/hardware.log` - GPIO and hardware logs
- `logs/errors.log` - Critical errors only
- `logs/performance.log` - Performance metrics (CSV format)

**System Logs**:
```bash
# Service logs
journalctl -u lightbox -f

# System logs
journalctl -f | grep lightbox
```

## Deployment Verification Checklist

### ✅ **Functional Verification**
- [ ] LED matrix displays animations correctly
- [ ] Web interface accessible at production URL
- [ ] All API endpoints responding properly
- [ ] Animation switching works smoothly
- [ ] Configuration changes persist correctly
- [ ] Health check endpoint reports healthy status

### ✅ **Performance Verification**
- [ ] System maintains target FPS consistently
- [ ] Memory usage within acceptable limits
- [ ] CPU usage under normal operating range
- [ ] No performance degradation over time
- [ ] Service restart under 15 seconds

### ✅ **Reliability Verification**
- [ ] Service auto-starts on system boot
- [ ] Automatic crash recovery working
- [ ] Error handling graceful and non-disruptive
- [ ] Logging comprehensive and useful
- [ ] No memory leaks detected

### ✅ **Security Verification**
- [ ] Service permissions correctly configured
- [ ] Web interface input validation working
- [ ] No sensitive data exposed
- [ ] Device access properly restricted

## Production Maintenance

### Regular Tasks
- **Daily**: Check service status and recent logs
- **Weekly**: Review performance logs and resource usage
- **Monthly**: Update dependencies and test backup procedures
- **Quarterly**: Full deployment verification re-run

### Monitoring Setup
```bash
# Add to crontab for automated health checks
0 */6 * * * curl -f http://192.168.0.222:5001/api/health > /dev/null || echo "LightBox health check failed" | mail admin@example.com
```

### Backup Procedures
```bash
# Backup configuration
cp settings.json settings.json.backup.$(date +%Y%m%d)

# Backup custom animations
tar -czf animations_backup_$(date +%Y%m%d).tar.gz scripts/

# Backup logs (if needed)
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

---

**Verification Completed By**: ________________  
**Date**: ________________  
**Production URL Tested**: http://192.168.0.222:5001  
**All Tests Passed**: ☐ Yes ☐ No  
**Notes**: _________________________________