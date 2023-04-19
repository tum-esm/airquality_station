# Airquality station

Raspberry pi code for the practical course "NOx sensor station".

**Initial raspberry setup:**

The following describes how the Rpi4 with a fresh SD-card should be set up to make the station work. The following steps are important:

-   Enable three UART ports to connect to the sensors
-   Rotate the screen and touch input on HDMI1
-   Install all python packages necessary to run the application

<br/>

## 1. Activate UART Ports

1. open the config file with 'sudo nano /boot/config.txt'
2. Add the following lines to the file:
    ```
    enable_uart=1
    dtoverlay=uart2
    dtoverlay=uart3
    dtoverlay=uart4
    ```
3. Save and close the file with 'Str + x'
4. Make sure that serial port 1 is not routed to the serial console. Check the raspberry pi config for this.
5. Reboot with `sudo reboot` to activate the changes.

<br/>

## 2. Configure Raspberry Screen

Since the display is rotated 180° one has to invert the display and then touch input. Furthermore, deactivate screen blanking. The Raspberry has two HDMI ports,

1. Open the raspberry pi screen utilities
2. Invert screen HDMI1
3. Follow these steps to invert the touchscreen
    1. Go to your terminal and type in `cd /usr/share/X11/xorg.conf.d/`
    2. List all files with `ls` and open the libinput file (e.g. 40-libinput.conf) with `sudo nano 40-libinput.conf`
    3. Find the InputClass section of the touchscreen and add the option "TransformationMatrix" as shown below:
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

<br/>

## 3. Initialize The Codebase

1. Install **git**, **python3.10** and **poetry**

https://git-scm.com/
https://python.org/
https://python-poetry.org/

2. Clone the repository and initialize submodule:

```bash
git clone https://github.com/tum-esm/airquality_station.git
cd airquality_station
git submodule init
git submodule update
```

3. Create a virtual environment

```bash
pip3 install --upgrade pip
python3.10 -m venv .venv
source .venv/bin/activate
```

4. Install the python dependencies

```bash
poetry install
```

5. Use `stv_client/client/config.example.json` to create a `stv_client/client/config.json` file
