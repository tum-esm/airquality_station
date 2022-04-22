# Airquality station
Raspberry pi code for the practical course "NOx sensor station".

# Initial raspberry setup
The following describes how the Rpi4 with a fresh SD-card should be set up to make the station work. Following steps are important: 
- Enable three UART ports to connect to the sensors
- Rotate the screen and touch input on HDMI1 
- Install all python packages necessary to run the application

### Activate UART Ports
1. open the config file with 'sudo nano /boot/config.txt'
2. Add following lines to the file: 
   ```
   enable_uart=1
   dtoverlay=uart2
   dtoverlay=uart3
   ```
3. Save and close the file with 'Str + x'
4. Make sure that the serial port 1 is not routed to the serial console. Check the raspberry pi config for this.
5. Reboot with `sudo reboot` to activate the changes. 

### Raspberry screen configuration
Since the display is rotated 180° one has to invert the display and then touch input. Furthermore, deactive screen blanking. The Raspberry has two HDMI ports, 
1. Open the raspberry pi screen utilities
2. Invert screen HDMI1
3. Follow these steps to invert the touchscreen
   1. Go to your terminal and type in `cd /usr/share/X11/xorg.conf.d/`
   2. List all files with `ls` and open the libinput file (e.g. 40-libinput.conf) with `sudo nano 40-libinput.conf`
   3. Find the InputClass section of touchscreen and add the option "TransformationMatrix" as shown below: 
   ```
   Section "InputClass"
         Identifier "libinput touchscreen catchall"
         MatchIsTouchscreen "on"
         Option "TransformationMatrix" "-1 0 1 0 -1 1 0 0 1"
         MatchDevicePath "/dev/input/event"
         Driver "libinput"
    EndSection
    ```
    4. reboot the device: `sudo reboot`

### Install python packages
``` bash 
sudo su -
apt-get update
apt-get install python3-matplotlib
apt-get install python3-scipy
apt-get install python3-pandas
pip3 install --upgrade pip
reboot
sudo pip3 install jupyter
```