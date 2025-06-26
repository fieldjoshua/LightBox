# LightBox Troubleshooting Guide

**Version**: 1.0  
**Last Updated**: 2025-06-23  
**For System Version**: Production v1.0

## Quick Diagnostic Commands

```bash
# System status overview
python3 service_manager.py status

# Health check
curl -s http://192.168.0.222:5001/api/health | python3 -m json.tool

# Hardware test
sudo python3 production_test.py

# Recent logs
python3 service_manager.py logs 20

# Test specific animation
python3 animation_test.py [animation_name]
```

## Common Issues and Solutions

### 🔴 **CRITICAL: No LED Output**

#### Symptoms
- Service running but no LED lights
- "pixels.show() NOT called" in logs
- Web interface works but no visual output

#### Diagnosis
```bash
# Check GPIO availability
ls -la /dev/gpio*
ls -la /dev/mem

# Check service user
sudo systemctl status lightbox | grep "Main PID"
ps aux | grep CosmicLED
```

#### Solutions
1. **Ensure sudo privileges**:
   ```bash
   sudo python3 service_manager.py stop
   sudo python3 CosmicLED.py  # Test manually
   ```

2. **Check service configuration**:
   ```bash
   sudo systemctl cat lightbox | grep User
   # Should show: User=root
   ```

3. **Verify GPIO permissions**:
   ```bash
   sudo usermod -a -G gpio $USER
   # Logout and login again
   ```

4. **Test hardware directly**:
   ```bash
   sudo python3 LightBox/scripts/matrix_test.py
   ```

---

### 🟠 **Color Range Errors**

#### Symptoms
- "byte must be in range(0, 256)" errors
- Animation crashes and falls back to cosmic
- Specific animations not working

#### Diagnosis
```bash
# Test all animations
python3 animation_test.py

# Test specific problematic animation
python3 animation_test.py hypnotic_cosmos 20
```

#### Solutions
1. **Update problematic animations**:
   - Already fixed in hypnotic_cosmos.py
   - Use color validation: `int(max(0, min(255, value)))`

2. **Check brightness values**:
   ```bash
   curl -s http://192.168.0.222:5001/api/config | grep brightness
   # Should be between 0.0 and 1.0
   ```

3. **Enable enhanced clamping**:
   - Enhanced clamp_pixels() function now active
   - Hardware-level validation implemented

---

### 🟠 **High CPU/Memory Usage**

#### Symptoms
- System sluggish
- CPU >90%
- Memory warnings in health check

#### Diagnosis
```bash
# Monitor resources
top -p $(pgrep -f CosmicLED.py)

# Check performance logs
tail -f logs/performance.log

# Health check
curl -s http://192.168.0.222:5001/api/health | grep -E "(cpu|memory)"
```

#### Solutions
1. **Reduce FPS**:
   ```bash
   curl -X POST http://192.168.0.222:5001/api/config \
     -H "Content-Type: application/json" \
     -d '{"fps": 15}'
   ```

2. **Switch to simpler animation**:
   ```bash
   curl -X POST http://192.168.0.222:5001/api/program \
     -H "Content-Type: application/json" \
     -d '{"program": "cosmic"}'
   ```

3. **Check for memory leaks**:
   ```bash
   # Monitor memory over time
   watch -n 5 'ps aux | grep CosmicLED | grep -v grep'
   ```

4. **Restart service if needed**:
   ```bash
   sudo python3 service_manager.py restart
   ```

---

### 🟡 **Web Interface Not Accessible**

#### Symptoms
- Connection refused on port 5001
- Timeout when accessing web interface
- API endpoints not responding

#### Diagnosis
```bash
# Check if port is open
sudo netstat -tlnp | grep 5001

# Check service status
python3 service_manager.py status

# Check web thread
sudo journalctl -u lightbox | grep "Web interface"
```

#### Solutions
1. **Check port conflicts**:
   ```bash
   # If port 5001 is used by another service
   sudo lsof -i :5001
   
   # Change port in config
   curl -X POST http://localhost:OTHER_PORT/api/config \
     -H "Content-Type: application/json" \
     -d '{"web_port": 5002}'
   ```

2. **Firewall issues**:
   ```bash
   # Check if firewall is blocking
   sudo ufw status
   sudo ufw allow 5001
   ```

3. **Restart web service**:
   ```bash
   sudo python3 service_manager.py restart
   ```

---

### 🟡 **Service Won't Start**

#### Symptoms
- `systemctl start lightbox` fails
- Service immediately exits
- "failed" status in service manager

#### Diagnosis
```bash
# Check service logs
python3 service_manager.py logs 50

# Check systemd logs
sudo journalctl -u lightbox -n 20

# Test manual start
cd /home/fieldjoshua/LightBox
sudo ./venv/bin/python3 CosmicLED.py
```

#### Solutions
1. **Fix path issues**:
   ```bash
   # Update service paths
   sudo python3 service_manager.py install
   ```

2. **Check dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Permission issues**:
   ```bash
   # Check file permissions
   ls -la CosmicLED.py
   chmod +x CosmicLED.py
   ```

4. **Configuration errors**:
   ```bash
   # Test config loading
   python3 -c "from config import Config; c = Config(); print('Config OK')"
   ```

---

### 🟡 **Animation Stuck/Frozen**

#### Symptoms
- Same frame showing repeatedly
- FPS shows 0 in status
- No animation updates

#### Diagnosis
```bash
# Check frame count progression
curl -s http://192.168.0.222:5001/api/status | grep frame_count
# Wait 5 seconds
curl -s http://192.168.0.222:5001/api/status | grep frame_count
# Frame count should increase
```

#### Solutions
1. **Restart animation**:
   ```bash
   curl -X POST http://192.168.0.222:5001/api/program \
     -H "Content-Type: application/json" \
     -d '{"program": "cosmic"}'
   ```

2. **Check for infinite loops in animation**:
   ```bash
   # Test animation separately
   python3 animation_test.py [stuck_animation]
   ```

3. **Service restart**:
   ```bash
   sudo python3 service_manager.py restart
   ```

---

## Advanced Diagnostics

### Log Analysis

#### Error Pattern Recognition
```bash
# Check for common error patterns
grep -i "error\|exception\|failed" logs/lightbox.log | tail -10

# Check color range errors specifically
grep "byte must be in range" logs/lightbox.log | wc -l

# Check hardware initialization
grep "LED matrix initialized" logs/lightbox.log | tail -1
```

#### Performance Analysis
```bash
# Check FPS trends
tail -100 logs/performance.log | cut -d',' -f1 | sort -n

# Check memory usage trends
tail -100 logs/performance.log | cut -d',' -f2 | sort -n

# Find performance anomalies
awk -F',' '$2 > 400 { print "High memory:", $0 }' logs/performance.log
```

### Hardware Debugging

#### GPIO Pin Testing
```bash
# Check GPIO pin status
sudo cat /sys/kernel/debug/gpio

# Test specific pin (GPIO18)
echo 18 | sudo tee /sys/class/gpio/export
echo out | sudo tee /sys/class/gpio/gpio18/direction
echo 1 | sudo tee /sys/class/gpio/gpio18/value  # LED should respond
echo 0 | sudo tee /sys/class/gpio/gpio18/value
echo 18 | sudo tee /sys/class/gpio/unexport
```

#### LED Strip Testing
```bash
# Manual LED test
sudo python3 -c "
import board
import neopixel
pixels = neopixel.NeoPixel(board.D12, 100, brightness=0.1)
pixels.fill((255, 0, 0))  # Red
pixels.show()
"
```

### System Resource Monitoring

#### Continuous Monitoring
```bash
# Monitor system resources
watch -n 1 'echo "=== System ===" && top -bn1 | head -5 && echo "=== LightBox ===" && ps aux | grep CosmicLED | grep -v grep && echo "=== Memory ===" && free -h'

# Monitor network connections
watch -n 2 'sudo netstat -tlnp | grep 5001'

# Monitor GPIO usage
watch -n 1 'ls -la /dev/gpio* /dev/mem 2>/dev/null'
```

#### Performance Benchmarking
```bash
# Benchmark animation performance
python3 -c "
import time
from config import Config
from CosmicLED import LEDMatrix
config = Config()
matrix = LEDMatrix(config)
start_time = time.time()
for i in range(300):  # 10 seconds at 30fps
    if matrix.current_program:
        matrix.current_program.animate(matrix.pixels, config, i)
    time.sleep(1/30)
end_time = time.time()
print(f'Performance: {300/(end_time-start_time):.1f} fps')
"
```

## Recovery Procedures

### Complete System Reset
```bash
# 1. Stop all services
sudo python3 service_manager.py stop

# 2. Clear all logs
rm -rf logs/*

# 3. Reset configuration to defaults
mv settings.json settings.json.backup
python3 -c "from config import Config; Config().save_config()"

# 4. Restart service
sudo python3 service_manager.py start

# 5. Verify operation
python3 service_manager.py status
curl -s http://192.168.0.222:5001/api/health
```

### Emergency LED Shutoff
```bash
# Immediate LED shutoff (if needed)
sudo python3 -c "
try:
    import board
    import neopixel
    pixels = neopixel.NeoPixel(board.D12, 100)
    pixels.fill((0, 0, 0))
    pixels.show()
    print('LEDs cleared')
except:
    print('Could not clear LEDs - check GPIO access')
"
```

### Service Recovery
```bash
# Reset systemd service
sudo python3 service_manager.py uninstall
sudo python3 service_manager.py install
sudo python3 service_manager.py start
```

## Prevention and Maintenance

### Regular Health Checks
```bash
# Add to crontab for automated monitoring
crontab -e
# Add: 0 */4 * * * /home/fieldjoshua/LightBox/health_check.sh
```

Create health_check.sh:
```bash
#!/bin/bash
cd /home/fieldjoshua/LightBox
HEALTH=$(curl -s http://192.168.0.222:5001/api/health | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
if [ "$HEALTH" != "healthy" ]; then
    echo "LightBox unhealthy - attempting restart"
    sudo python3 service_manager.py restart
fi
```

### Log Rotation
```bash
# Setup log rotation
sudo tee /etc/logrotate.d/lightbox << EOF
/home/fieldjoshua/LightBox/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 fieldjoshua fieldjoshua
    postrotate
        sudo systemctl reload lightbox 2>/dev/null || true
    endscript
}
EOF
```

### Performance Monitoring
```bash
# Monitor resource usage trends
python3 -c "
import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv('logs/performance.log', names=['timestamp', 'fps', 'memory', 'cpu', 'frames'])
df.plot(x='timestamp', y=['fps', 'memory', 'cpu'])
plt.savefig('performance_trend.png')
print('Performance chart saved to performance_trend.png')
"
```

## Getting Help

### Information to Collect
When reporting issues, collect:

```bash
# System information
uname -a
python3 --version
cat /etc/os-release

# LightBox status
python3 service_manager.py status
curl -s http://192.168.0.222:5001/api/health

# Recent logs
python3 service_manager.py logs 50

# Configuration
cat settings.json

# Hardware information
lscpu | head -10
free -h
df -h
```

### Contact Information
- **Documentation**: Check CLAUDE.md and README.md
- **Issue Tracking**: Create GitHub issue with collected information
- **Emergency**: Use emergency LED shutoff procedure above

---

**Last Updated**: 2025-06-23  
**Document Version**: 1.0  
**Tested On**: Raspberry Pi 4, Raspberry Pi Zero W