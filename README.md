# Airquality station
Raspberry pi code for the practical course "NOx sensor station".
This repository holds everything necessary for the course

# Raspberry setup
The station uses three UART ports on the Raspberry pi. They need to be
activated in the raspberry config file: 

1. open the config file with 'sudo nano /boot/config.txt'
2. add following lines to the file: 'enable_uart =1', 'dtoverlay=uart2', 
'dtoverlay=uart3'
3. Save and close the file with 'Str + x'
