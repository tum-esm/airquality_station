# Airquality station
Raspberry pi code for the practical course "NOx sensor station".

# Initial raspberry setup
The following describes how the Rpi4 with a fresh SD-card should be set up to make the station work. Following steps are important: 
- Enable three UART ports to connect to the sensors
- Rotate the screen and touch input on HDMI1 
- Install all python packages necessary to run the application

### Activate UART Ports
1. open the config file with 'sudo nano /boot/config.txt'
2. Add following lines to the file: `enable_uart=1`, `dtoverlay=uart2`, `dtoverlay=uart3`. 
3. Save and close the file with 'Str + x'
4. Make sure that the serial port 1 is not routed to the serial console. Check the raspberry pi config for this.
5. Reboot with `sudo reboot` to activate the changes. 

### Raspberry screen configuration
Since the display is rotated 180° one has to invert the display and then touch input. Furthermore, deactive screen blanking. The Raspberry has two HDMI ports, 
1. Open the raspberry pi screen utilities
2. invert the screen
3. Follow this instruction (link instruction) to invert the touch input. 

### Install python packages
-> coming soon