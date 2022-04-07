import ec_sense
from guizero import App, Box, Text, PushButton, CheckBox
from datetime import date, datetime


#set main colors
main_bg = "#E5E5EA"
sub_bg = "#8E8E93"
main_text_col = "#1C1C26"
main_font = "Arial"

# some default values
nox = 0
temp = 0
humid = 0

def start():
    start_button.disable()
    stop_button.enable()
    start_button.bg="green"
    
def stop():
    start_button.enable()
    stop_button.disable()
    stop_button.bg="red"
    

# display display_size = 800x480 px
# four quadrant box layout
app = App(title="AirQ v1.0 ", layout = 'grid', visible=True, bg="white")
app.bg = main_bg
app.text_color = main_text_col
app.font = main_font


# indicator box holds all indicated values
indicator = Box(app, grid = [0,0])
indicator.bg = sub_bg
indicator.set_border(20, main_bg)

#indicated values and descriptive texts
Text(indicator, text = "Sensor values", size = 10, color = "white")

indicator_sub = Box(indicator, layout = "grid")
indicator_sub.set_border(5, sub_bg)

nox_ind = Text(indicator_sub, text = nox, color = 'white', size = 20, grid = [0,0])
temp_ind = Text(indicator_sub, text = temp, color = 'white', size = 20, grid = [0,1])
humid_ind = Text(indicator_sub, text = humid, color = 'white', size = 20, grid = [0,2])
Text(indicator_sub, text = " ppm NOx", align = "left", grid = [1,0])
Text(indicator_sub, text = " °C", align = "left", grid = [1,1])
Text(indicator_sub, text = " % rH", align = "left", grid = [1,2])

# used to set system settings
settings = Box(app, grid = [1,0])
settings.set_border(20, main_bg)

#indicated values and descriptive texts
Text(settings, text = "Settings", size = 10, color = main_text_col)
settings_sub = Box(settings)#, layout = "grid")
settings_sub.set_border(5, main_bg)

start_button = PushButton(settings_sub, command = start, text="start")
stop_button = PushButton(settings_sub, command = stop, text="stop", enabled = False)


# status boxes
status = Box(app, grid=[1,1])

CheckBox(status, text = "test", enabled= True)

# messages box shows warnigs and messages from the system
messages = Box(app, layout = "grid", grid = [0,1])



# run as main application
if __name__ == "__main__":
    app.display()
