# volumio_hdmi_cec
HDMI CEC for controlling the LG BD PLAYER and TV

LG BD PLAYER (shown as BD-HTS) uses CEC DEVICE 5 (audio) to communicate
LG BD PLAYER does *not* support 15:82 or turn_on cmd, hence using hack 15:44:40 (power button hit) to turn on
LG BD PLAYER does *not* support 1f:82 (set active), hence using 15:44:24 (changing input source button pressed) to change source

RPI attached to `HDMI-IN1` (input-source button hit 4 times)

TV attached to `OPTICAL` and `HDMI-IN2` or `HDMI-OUT`. The program switch to `OPTICAL` once TV turned on.

# USAGE
```
python3 -m venv venv
source ./venv/bin/activate

pip install -r ./requirements.txt
sudo python3 ./volumio_controller.py
```

# LOG

LOGGING default writes to `/var/log/hdmi-cec.log`, with level to `INFO`
