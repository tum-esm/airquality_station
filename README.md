# Airquality station
Raspberry pi code for the practical course "NOx sensor station".

# Initial raspberry setup
The station uses three UART ports on the Raspberry pi. They need to be activated in the raspberry config file: 

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
