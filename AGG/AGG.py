import tkinter as tk
import re
import math
import serial
import time
import queue

# Queue to store GUI dataframes
gui_queue = queue.Queue()

class SerialComm:
    def __init__(self, port, baudrate = 19200):
        self.ser = serial.Serial(port)
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS    # number of bits per bytes # SEVENBITS
        self.ser.parity = serial.PARITY_NONE    # set parity check: no parity # PARITY_ODD
        self.ser.stopbits = serial.STOPBITS_ONE # number of stop bits # STOPBITS_TWO
        #self.ser.timeout = None                # block read
        self.ser.timeout = 1                    # non-block read
        #self.ser.timeout = 2                   # timeout block read
        self.ser.xonxoff = False                # disable software flow control
        self.ser.rtscts = False                 # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False                 # disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2               # timeout for write
        
        self.dataReceived = None

        self.ack = 0

        self.ser.flushInput()  # flush input buffer, discarding all its contents
        self.ser.flushOutput() # flush output buffer, aborting current output and discard all that is in buffer

    def read(self):
        if self.ser.in_waiting > 0:
            self.dataReceived = self.ser.readline().decode('ascii')

            self.ser.flushInput()  # flush input buffer, discarding all its contents
            self.ser.flushOutput() # flush output buffer, aborting current output and discard all that is in buffer

            return self.dataReceived

    def write(self, message):
        self.ser.write(message.encode())
        #time.sleep(0.1)

    def close(self):
        self.ser.close()

class DataFrame:
    def __init__(self, window,canvas, network, routes, width, height):
        self.canvas = canvas
        self.window = window
        self.data = {}
        self.text_id = None
        self.width = width
        self.height = height
        self.newEvent = False

        self.dataSent = None
        self.dataReceived = None
        self.dataGUI = None

        for ne in network:
            if 'Occupation' not in self.data:
                self.data['Occupation'] = {}
            self.data['Occupation'][ne] = 1

        for route in routes:
            if 'Routes' not in self.data:
                self.data['Routes'] = {}
            self.data['Routes'][f'R{route}'] = 0

        for ne in network:
            if 'Signal' in network[ne]:
                if 'Signal' not in self.data:
                    self.data['Signal'] = {}
                for signal in network[ne]['Signal']:
                    self.data['Signal'][signal] = 0
        
            if 'LevelCrossing' in network[ne]:
                if 'LevelCrossing' not in self.data:
                    self.data['LevelCrossing'] = {}
                for levelCrossing in network[ne]['LevelCrossing']:
                    self.data['LevelCrossing'][levelCrossing] = 1
         
            if 'Switch' in network[ne]:
                if 'Switch' not in self.data:
                    self.data['Switch'] = {}
                for switch in network[ne]['Switch']:
                    self.data['Switch'][switch] = 0
            if 'Switch_B' in network[ne]:
                if 'Switch' not in self.data:
                    self.data['Switch'] = {}
                for switch in network[ne]['Switch_B']:
                    self.data['Switch'][switch] = 0
            if 'Switch_C' in network[ne]:
                if 'Switch' not in self.data:
                    self.data['Switch'] = {}
                for switch in network[ne]['Switch_C']:
                    self.data['Switch'][switch] = 0

        for ne in network:
            if 'Switch_X' in network[ne]:
                if 'Switch' not in self.data:
                    self.data['Switch'] = {}
                for switch in network[ne]['Switch_X']:
                    self.data['Switch'][switch] = 0

        for ne in network:
            if 'Crossing' in network[ne]:
                if 'Switch' not in self.data:
                    self.data['Switch'] = {}
                for switch in network[ne]['Crossing']:
                    self.data['Switch'][switch] = 0

        self.occupationFrame = ''.join([str(value) for value in self.data['Occupation'].values()])
        self.routeFrame = ''.join([str(value) for value in self.data['Routes'].values()])
        self.signalFrame = ''.join([str(value) for value in self.data['Signal'].values()])
    
        if 'LevelCrossing' in self.data:
            self.levelCrossingFrame = ''.join([str(value) for value in self.data['LevelCrossing'].values()])
        else:
            self.levelCrossingFrame = None

        self.switchFrame = ''.join([str(value) for value in self.data['Switch'].values()])

        self.frame =  f'{self.occupationFrame}|{self.routeFrame}|{self.signalFrame}|{self.levelCrossingFrame}|{self.switchFrame}'
     
        self.update_text()

    def __str__(self):
        print(f'{self.data}')
        
        return f'{self.frame}'

    def update_text(self):
        self.occupationFrame = ''
        self.routeFrame = ''
        self.signalFrame = ''
        self.levelCrossingFrame = ''
        self.switchFrame = ''

        if 'Occupation' in self.data:
            self.occupationFrame = ''.join([str(value) for value in self.data['Occupation'].values()])
        if 'Routes' in self.data:
            self.routeFrame = ''.join([str(value) for value in self.data['Routes'].values()])
        if 'Signal' in self.data:
            self.signalFrame = ''.join([str(value) for value in self.data['Signal'].values()])
        if 'LevelCrossing' in self.data:
            self.levelCrossingFrame = ''.join([str(value) for value in self.data['LevelCrossing'].values()])
        if 'Switch' in self.data:
            self.switchFrame = ''.join([str(value) for value in self.data['Switch'].values()])

        self.frame =  f'<{self.occupationFrame}|{self.routeFrame}|{self.signalFrame}|{self.levelCrossingFrame}|{self.switchFrame}>'
        self.dataSent = f'<{self.occupationFrame}{self.routeFrame}{self.signalFrame}{self.levelCrossingFrame}{self.switchFrame}>'

        self.window.title(self.frame)
      
class NetElement:
    def __init__(self, canvas,dataFrame,x1, y1, x2, y2, net_elements, net_element_key, color='black'):
        self.id = canvas.create_line(x1, y1, x2, y2, fill=color,width=5)
        self.pressed = False
        self.canvas = canvas
        self.net_elements = net_elements
        self.net_element_key = net_element_key
        self.dataFrame = dataFrame
        canvas.tag_bind(self.id, "<Button-1>", self.on_net_element_click)
        self.update_draw()

    def on_net_element_click(self, event):
        
        self.pressed = not self.pressed
        new_color = 'red' if self.pressed else 'black'
        for net_element in self.net_elements.values():
            event.widget.itemconfig(net_element.id, fill=new_color)

        value = int(self.dataFrame.data['Occupation'][self.net_element_key], 16)

        if self.pressed:
            #print(f'NetElement {self.net_element_key} is occupied')
            value &= ~1
        else:
            #print(f'NetElement {self.net_element_key} is released')
            value |= 1
        
        self.dataFrame.data['Occupation'][self.net_element_key] = format(value, 'x')
        self.dataFrame.newEvent = True
        self.dataFrame.update_text()
        self.update_draw()

    def update_draw(self):
        #print(self.dataFrame.data['Occupation'][self.net_element_key])
        match str(self.dataFrame.data['Occupation'][self.net_element_key]):
            case '0': #0000
                color = 'red'
            case '1': #0001
                color = 'black'
            case '4': #0100
                color = 'red2'
            case '5': #0101
                color = 'grey70'
            case '8': #1000
                color = 'red3'
            case '9': #1001
                color = 'grey60'

        self.canvas.itemconfig(self.id, fill=color)
        self.canvas.after(10, self.update_draw)

class BufferStop:
    def __init__(self, canvas, x, y, direction ,color='black'):
        sign = -1 if direction == '>' else 1
        self.id = canvas.create_line(x, y-25, x+sign*10, y-25,x, y-25, x, y+25,x, y+25, x+sign*10, y+25, fill=color,width=3)
        
class Border:
    def __init__(self, canvas, x, y, direction ,color='black'):
        sign = 1 if direction == '>' else -1
        self.id = None
        canvas.create_line(x+sign*5, y, x+sign*10, y, fill=color,width=3)
        canvas.create_line(x+sign*15, y, x+sign*20, y, fill=color,width=3)

class RailJoint:
    def __init__(self, canvas, x, y, color='black'):
        self.id = None
        canvas.create_line(x+10, y+15, x+10 , y-15, fill=color,width=3)
        canvas.create_line(x-10, y+15, x-10 , y-15, fill=color,width=3)

class Platform:
    def __init__(self, canvas, x, y, alignment ,color='red'):
        self.id = None

        if alignment == 'top':
            canvas.create_line(x-75, y-15, x+75, y-15, fill=color,width=3)
            canvas.create_line(x-75, y-15, x-75, y-45, fill=color,width=3)
            canvas.create_line(x+75, y-15, x+75, y-45, fill=color,width=3)
            canvas.create_line(x-75, y-30, x+75, y-30, fill=color,width=3)
        else:
            canvas.create_line(x-75, y+15, x+75, y+15, fill=color,width=3)
            canvas.create_line(x-75, y+15, x-75, y+45, fill=color,width=3)
            canvas.create_line(x+75, y+15, x+75, y+45, fill=color,width=3)
            canvas.create_line(x-75, y+30, x+75, y+30, fill=color,width=3)

class LevelCrossing:
    def __init__(self, canvas,dataFrame, x, y ,levelCrossings,levelCrossing_key,color='blue'):
        self.levelCrossings = levelCrossings
        self.levelCrossing_key = levelCrossing_key
        self.dataFrame = dataFrame
        self.canvas = canvas

        # Create lines and store their ids
        self.ids = [
            canvas.create_line(x+30, y-60, x+30, y+60, fill=color,width=3),
            canvas.create_line(x+30, y-60, x+45, y-75, fill=color,width=3),
            canvas.create_line(x+30, y+60, x+45, y+75, fill=color,width=3),
            canvas.create_line(x-30, y-60, x-30, y+60, fill=color,width=3),
            canvas.create_line(x-30, y-60, x-45, y-75, fill=color,width=3),
            canvas.create_line(x-30, y+60, x-45, y+75, fill=color,width=3)
        ]

        # Bind the click event to all lines
        for id in self.ids:
            self.canvas.tag_bind(id, "<Button-1>", self.on_net_element_click)
        self.update_draw()

    def update_draw(self):
        #print(self.dataFrame.data['LevelCrossing'])

        match str(self.dataFrame.data['LevelCrossing'][self.levelCrossing_key]):
            case '0': #0000
                color = 'red'
            case '1': #0001
                color = 'blue'
            case '4': #0100
                color = 'red2'
            case '5': #0101
                color = 'blue2'
            case '8': #1000
                color = 'red3'
            case '9': #1001
                color = 'blue4'

        for id in self.ids:
            self.canvas.itemconfig(id, fill=color)
        self.canvas.after(10, self.update_draw)
        
    def on_net_element_click(self, event):

        value = int(self.dataFrame.data['LevelCrossing'][self.levelCrossing_key], 16)
        value ^= 1
        self.dataFrame.data['LevelCrossing'][self.levelCrossing_key] = format(value, 'x')

        self.dataFrame.newEvent = True
        self.dataFrame.update_text()
        self.update_draw()

class Border:
    def __init__(self, canvas, x, y, direction ,color='black'):
        sign = 1 if direction == '>' else -1
        self.id = None
        canvas.create_line(x+sign*5, y, x+sign*10, y, fill=color,width=3)
        canvas.create_line(x+sign*15, y, x+sign*20, y, fill=color,width=3)

class Signals:
    def __init__(self, canvas,dataFrame, x, y ,name,way,net_coordinate = None,other_signals=None ,signals = None, color='grey' ):
        font_size = 8
        self.pressed = False
        self.signals = signals
        self.canvas = canvas
        self.color = color
        self.other_signals = tuple(other_signals.keys()) if other_signals else ()
        self.routes = other_signals if other_signals else {}
        self.dataFrame = dataFrame
        self.signal_key = name
        # next_signals = tuple(signal_routes[name].keys())

        direction = name[-2]
        side = name[-1]
        self.name = name[:-2]

        if net_coordinate != None:
            slope = 'up' if (net_coordinate[1][1] - net_coordinate[0][1]) / (net_coordinate[1][0] - net_coordinate[0][0]) > 0 else 'down'
            #print(f'{name} {x} {y} {net_coordinate} {way} {slope}')

        x0 = -1
        y0 = 1
        r = 15

        if net_coordinate == None:
            if direction == 'l' and side == 'n':
                #color = 'red'
                x0 = -1
                y0 = 1
            if direction == 'l' and side == 'r':
                #color = 'green'
                x0 = -1
                y0 = 1
            if direction == 'r' and side == 'n':
                #color = 'blue'
                x0 = -1
                y0 = 1
            if direction == 'r' and side == 'r':
                #color = 'black'
                x0 = 1
                y0 = -1

            x0 = x0 if way == '>' else -x0
            y0 = y0 if way == '>' else -y0

            self.id = canvas.create_text(x,y-(y0*55),text=name[:-2],fill=color,font=font_size)
            self.semaphore = [ 
                canvas.create_line(x, (y-y0*30), (x-x0*25), (y-y0*30), fill=color,width=3),
                canvas.create_line(x, (y-y0*30)+10, x, (y-y0*30)-10, fill=color,width=3),
                canvas.create_oval((x-x0*40)-r,(y-y0*30)-r,(x-x0*40)+r,(y-y0*30)+r,outline=color,width=3)
            ]

        else:
            x0 = 0
            y0 = 0
            if slope == 'up' and way == '>':
                #color = 'orange'
                self.id =  canvas.create_text(x+70, y+25, text=name, fill=color, font=font_size)
                self.semaphore = [ 
                    canvas.create_line(x+30, y+9, x+49, y-14, fill=color,width=3),
                    canvas.create_line(x+60, y-5, x+38, y-22, fill=color,width=3),
                    canvas.create_oval((x+20)-r, (y+20)-r, (x+20)+r, (y+20)+r, outline=color, width=3)
                ]
            if slope == 'up' and way == '<':
                color = 'grey'
            if slope == 'down' and way == '>':
                #color = 'pink'
                self.id =  canvas.create_text(x+100, y-25, text=name, fill=color, font=font_size)
                self.semaphore = [ 
                    canvas.create_line(x+82, y+8, x+55, y-16, fill=color,width=3),
                    canvas.create_line(x+45, y-5, x+65, y-25, fill=color,width=3),
                    canvas.create_oval((x+90)-r, (y+20)-r, (x+90)+r, (y+20)+r, outline=color, width=3)
                ]
            if slope == 'down' and way == '<':
                #color = 'cyan'
                self.id = canvas.create_text(x-100, y+45, text=name, fill=color, font=font_size)
                self.semaphore = [ 
                    canvas.create_line(x-55, y+35, x-79, y+10, fill=color,width=3),
                    canvas.create_line(x-65, y+35+10, x-45, y+35-10, fill=color,width=3),
                    canvas.create_oval((x-90)-r, y-r, (x-90)+r, y+r, outline=color, width=3)
                ]
        canvas.tag_bind(self.id, "<Button-1>", self.on_signal_click)
        self.update_draw()

    def update_draw(self):
        #print(self.dataFrame.data['Signal'][self.signal_key])

        match str(self.dataFrame.data['Signal'][self.signal_key]):
            case '0': #0000
                color = 'red'
            case '1': #0001
                color = 'orange'
            case '2': #0010
                color = 'yellow'
            case '3': #0011
                color = 'green'

            case '4': #0100
                color = 'red'
            case '5': #0101
                color = 'orange'
            case '6': #0110
                color = 'yellow'
            case '7': #0111
                color = 'green'

            case '8': #1000
                color = 'red'
            case '9': #1001
                color = 'orange'
            case 'A': #1010
                color = 'yellow'
            case 'B': #1011
                color = 'green'

        self.canvas.itemconfig(self.semaphore[-3], fill=color)
        self.canvas.itemconfig(self.semaphore[-2], fill=color)
        self.canvas.itemconfig(self.semaphore[-1], fill=color,outline=color)

        self.canvas.after(10, self.update_draw)

    def on_signal_click(self, event):
        self.pressed = not self.pressed

        for signal_name in self.signals:
            signal = self.signals[signal_name]

            match self.color:
                case 'grey':
                    if signal_name == self.name:
                        print(f'Signal {self.name} is selected')
                        color = 'green'
                        self.canvas.itemconfig(self.id, fill=color)

                    if signal_name in self.other_signals:
                        signal.color = 'red'
                        signal.canvas.itemconfig(signal.id, fill=signal.color)
                    else:
                        if signal_name != self.name:
                            signal.color = 'grey70'
                            signal.canvas.itemconfig(signal.id, fill=signal.color)
                            signal.canvas.tag_unbind(signal.id, "<Button-1>")
                case 'green':
                    if signal_name == self.name:
                        routes = list(signal.routes.values())
                        #self.dataFrame.newEvent = True
                        print(f'Signal {self.name} is released [{routes}]')
                        
                        for route in routes:
                            self.dataFrame.data['Routes'][route] = 9
                        self.dataFrame.newEvent = True
                        self.dataFrame.update_text()
                        color = 'grey'
                        self.canvas.itemconfig(self.id, fill=color)
                    if signal_name in self.other_signals:
                        signal.color = 'grey'
                        signal.canvas.itemconfig(signal.id, fill=signal.color)
                    else:
                        if signal_name != self.name:
                            signal.color = 'grey'
                            signal.canvas.itemconfig(signal.id, fill=signal.color)
                            signal.canvas.tag_bind(signal.id, "<Button-1>", signal.on_signal_click)
                case 'red':
                    if signal_name == self.name:
                        #print(f'Route {self.name} {self.routes} is launched')
                        color = 'grey'
                        self.canvas.itemconfig(self.id, fill=color)
                    else:
                        color = 'grey'
                        if signal.color == 'green':
                            route = signal.routes[self.name]
                            print(f'Route {route} launched')
                            self.dataFrame.data['Routes'][route] = 1
                            self.dataFrame.newEvent = True
                            self.dataFrame.update_text()
                        signal.color = 'grey'
                        signal.canvas.itemconfig(signal.id, fill=signal.color)
                        signal.canvas.tag_bind(signal.id, "<Button-1>", signal.on_signal_click)
                case _:
                    color = 'grey'
                    self.canvas.itemconfig(self.id, fill=color)

        self.color = color
            
class Switch:
    def __init__(self, canvas,dataFrame, width,height, switches_pos, switch_key,switches, color='black'):
        r = 15
        self.switches = switches
        self.switch_key = switch_key
        self.dataFrame = dataFrame
        self.canvas = canvas
        self.width = width
        self.height = height

        if len(switches_pos[switch_key]) == 4:
            self.type = 'simple'
            self.core = self.convert_coordinates(switches_pos[switch_key][0][0],switches_pos[switch_key][0][1])
            self.start = self.convert_coordinates(switches_pos[switch_key][1][0],switches_pos[switch_key][1][1])
            self.branch = self.convert_coordinates(switches_pos[switch_key][2][0],switches_pos[switch_key][2][1])
            self.cont = self.convert_coordinates(switches_pos[switch_key][3][0],switches_pos[switch_key][3][1])

            #print(f'{switch_key} | {switches_pos[switch_key]} | {self.core}')

            self.ids = [
            #canvas.create_oval(self.core[0]-r, self.core[1]-r, self.core[0]+r, self.core[1]+r, outline='white', width=3, fill = 'white'),
            canvas.create_line(self.core[0], self.core[1], self.start[0], self.start[1], fill=color, width=5),
            canvas.create_line(self.core[0], self.core[1], self.branch[0], self.branch[1], fill='white', width=5),
            canvas.create_line(self.core[0], self.core[1], self.cont[0], self.cont[1], fill=color, width=5)
            ]
            
            self.canvas = canvas
            self.previous_items = set(self.canvas.find_all())
            self.check_for_changes()
            # Bind the click event to all lines
            for id in self.ids:
                canvas.tag_bind(id, "<Button-1>", self.switch_position)

        if len(switches_pos[switch_key]) == 5 and switches_pos[switch_key][0] != (0,0):
            self.type = 'double'
            self.state = 0

            self.core = self.convert_coordinates(switches_pos[switch_key][0][0],switches_pos[switch_key][0][1])

            coordinates = switches_pos[switch_key][1:]
            coordinates.sort(key=lambda coord: coord[0])

            # Separate the coordinates with the same y as the core and the others
            same_y = [coord for coord in coordinates if coord[1] == switches_pos[switch_key][0][1]]
            different_y = [coord for coord in coordinates if coord[1] != switches_pos[switch_key][0][1]]

            # The points with the same y as the core are the normal points
            self.normalL = self.convert_coordinates(same_y[0][0],same_y[0][1])
            self.normalR = self.convert_coordinates(same_y[1][0],same_y[1][1])

            # The other points are the branch points
            #print(f'{different_y[0][0]},{different_y[0][1]} {different_y[1][0]},{different_y[1][1]}')

            self.branchL = self.convert_coordinates(different_y[0][0],different_y[0][1])
            self.branchR = self.convert_coordinates(different_y[1][0],different_y[1][1])
            
            '''
            if different_y[0][1] < different_y[1][1]:
                self.branchL = self.convert_coordinates(different_y[0][0],different_y[0][1])
                self.branchR = self.convert_coordinates(different_y[1][0],different_y[1][1])
            else:
                self.branchR = self.convert_coordinates(different_y[0][0],different_y[0][1])
                self.branchL = self.convert_coordinates(different_y[1][0],different_y[1][1])
            '''
            #print(f'{switch_key} | {switches_pos[switch_key]} | {self.core}')

            self.ids = [
            canvas.create_oval(self.core[0]-r, self.core[1]-r, self.core[0]+r, self.core[1]+r, outline='white', width=3, fill = 'white'),
            canvas.create_line(self.core[0], self.core[1], self.normalL[0], self.normalL[1], fill='white', width=5),
            canvas.create_line(self.core[0], self.core[1], self.normalR[0], self.normalR[1], fill='white', width=5),
            canvas.create_line(self.core[0], self.core[1], self.branchL[0], self.branchL[1], fill=color, width=5),
            canvas.create_line(self.core[0], self.core[1], self.branchR[0], self.branchR[1], fill=color, width=5)
            ]
            
            self.canvas = canvas
            self.previous_items = set(self.canvas.find_all())
            self.check_for_changes()
            # Bind the click event to all lines
            for id in self.ids:
                canvas.tag_bind(id, "<Button-1>", self.switch_position)

        if len(switches_pos[switch_key]) == 5 and switches_pos[switch_key][0] == (0,0):
            self.type = 'scissor'
            self.state = 0

            #print(f'{switch_key} | {switches_pos[switch_key]} | {self.core}')

            self.BranchUpRight      = self.convert_coordinates(switches_pos[switch_key][1][0],switches_pos[switch_key][1][1])
            self.BranchUpLeft       = self.convert_coordinates(switches_pos[switch_key][2][0],switches_pos[switch_key][2][1])
            self.BranchDownLeft     = self.convert_coordinates(switches_pos[switch_key][3][0],switches_pos[switch_key][3][1])
            self.BranchDownRight    = self.convert_coordinates(switches_pos[switch_key][4][0],switches_pos[switch_key][4][1])

            self.ids = [
            #canvas.create_oval(self.core[0]-r, self.core[1]-r, self.core[0]+r, self.core[1]+r, outline='white', width=3, fill = 'white'),
            canvas.create_line(self.BranchUpLeft[0], self.BranchUpLeft[1], self.BranchDownRight[0], self.BranchDownRight[1], fill='white', width=5),
            canvas.create_line(self.BranchUpRight[0], self.BranchUpRight[1], self.BranchDownLeft[0], self.BranchDownLeft[1], fill=color, width=5)
            ]
            
            self.canvas = canvas
            self.previous_items = set(self.canvas.find_all())
            self.check_for_changes()
            # Bind the click event to all lines
            for id in self.ids:
                canvas.tag_bind(id, "<Button-1>", self.switch_position)

        self.update_draw()

    def update_draw(self):
        #print(self.dataFrame.data['Switch'])
        if self.type == 'simple':

            match str(self.dataFrame.data['Switch'][self.switch_key]):
                case '0': #0000
                    main_color = 'black'
                    normal_color = 'black'
                    reverse_color = 'white'
                    normal_width = 5
                    reverse_width = 6
                    index = -1
                case '1': #0001
                    main_color = 'black'
                    normal_color = 'white'
                    reverse_color = 'black'
                    normal_width = 6
                    reverse_width = 5
                    index = -2
                case '4': #0100
                    main_color = 'grey70'
                    normal_color = 'grey70'
                    reverse_color = 'white'
                    normal_width = 5
                    reverse_width = 6
                    index = -1
                case '5': #0101
                    main_color = 'grey70'
                    normal_color = 'white'
                    reverse_color = 'grey70'
                    normal_width = 6
                    reverse_width = 5
                    index = -2
                case '8': #1000
                    main_color = 'grey60'
                    normal_color = 'grey60'
                    reverse_color = 'white'
                    normal_width = 5
                    reverse_width = 6
                    index = -1
                case '9': #1001
                    main_color = 'grey60'
                    normal_color = 'white'
                    reverse_color = 'grey60'
                    normal_width = 6
                    reverse_width = 5
                    index = -2

            self.canvas.itemconfig(self.ids[-2], fill=reverse_color, width = reverse_width)
            self.canvas.itemconfig(self.ids[-1], fill=normal_color, width = normal_width)
            self.canvas.itemconfig(self.ids[0], fill=main_color)
            self.canvas.tag_raise(self.ids[index])

        if self.type == 'double':
    
            match str(self.dataFrame.data['Switch'][self.switch_key]):
                case '0': #0000 NN
                    color_4 = 'black'
                    color_3 = 'black'
                    color_2 = 'white'
                    color_1 = 'white'
                    width_4 = 5
                    width_3 = 5
                    width_2 = 6
                    width_1 = 6
                    index_A = -4
                    index_B = -3
                case '1': #0001 RR
                    color_4 = 'white'
                    color_3 = 'white'
                    color_2 = 'black'
                    color_1 = 'black'
                    width_4 = 6
                    width_3 = 6
                    width_2 = 5
                    width_1 = 5
                    index_A = -2
                    index_B = -1
                case '2': #0010 RN
                    color_4 = 'white'
                    color_3 = 'black'
                    color_2 = 'black'
                    color_1 = 'white'
                    width_4 = 6
                    width_3 = 5
                    width_2 = 5
                    width_1 = 6
                    index_A = -3
                    index_B = -2                
                case '3': #0011 NR
                    color_4 = 'black'
                    color_3 = 'white'
                    color_2 = 'white'
                    color_1 = 'black'
                    width_4 = 5
                    width_3 = 6
                    width_2 = 6
                    width_1 = 5
                    index_A = -4
                    index_B = -1
                case '4': #0100
                    color_4 = 'grey70'
                    color_3 = 'grey70'
                    color_2 = 'white'
                    color_1 = 'white'
                    width_4 = 5
                    width_3 = 5
                    width_2 = 6
                    width_1 = 6
                    index_A = -4
                    index_B = -3
                case '5': #0101
                    color_4 = 'white'
                    color_3 = 'white'
                    color_2 = 'grey70'
                    color_1 = 'grey70'
                    width_4 = 6
                    width_3 = 6
                    width_2 = 5
                    width_1 = 5
                    index_A = -2
                    index_B = -1
                case '6': #0110
                    color_4 = 'white'
                    color_3 = 'grey70'
                    color_2 = 'grey70'
                    color_1 = 'white'
                    width_4 = 6
                    width_3 = 5
                    width_2 = 5
                    width_1 = 6
                    index_A = -3
                    index_B = -2 
                case '7': #0111
                    color_4 = 'grey70'
                    color_3 = 'white'
                    color_2 = 'white'
                    color_1 = 'grey70'
                    width_4 = 5
                    width_3 = 6
                    width_2 = 6
                    width_1 = 5
                    index_A = -4
                    index_B = -1
                case '8': #1000
                    color_4 = 'grey60'
                    color_3 = 'grey60'
                    color_2 = 'white'
                    color_1 = 'white'
                    width_4 = 5
                    width_3 = 5
                    width_2 = 6
                    width_1 = 6
                    index_A = -4
                    index_B = -3
                case '9': #1001
                    color_4 = 'white'
                    color_3 = 'white'
                    color_2 = 'grey60'
                    color_1 = 'grey60'
                    width_4 = 6
                    width_3 = 6
                    width_2 = 5
                    width_1 = 5
                    index_A = -2
                    index_B = -1
                case 'A': #1010
                    color_4 = 'white'
                    color_3 = 'grey60'
                    color_2 = 'grey60'
                    color_1 = 'white'
                    width_4 = 6
                    width_3 = 5
                    width_2 = 5
                    width_1 = 6
                    index_A = -3
                    index_B = -2 
                case 'B': #1011
                    color_4 = 'grey60'
                    color_3 = 'white'
                    color_2 = 'white'
                    color_1 = 'grey60'
                    width_4 = 5
                    width_3 = 6
                    width_2 = 6
                    width_1 = 5
                    index_A = -4
                    index_B = -1

            self.canvas.itemconfig(self.ids[-4], fill = color_4, width = width_4)
            self.canvas.itemconfig(self.ids[-3], fill = color_3, width = width_3)
            self.canvas.itemconfig(self.ids[-2], fill = color_2, width = width_2)
            self.canvas.itemconfig(self.ids[-1], fill = color_1, width = width_1)
            self.canvas.tag_raise(self.ids[index_A])
            self.canvas.tag_raise(self.ids[index_B])

        if self.type == 'scissor':

            match str(self.dataFrame.data['Switch'][self.switch_key]):
                case '0': #0000
                    normal_color = 'white'
                    reverse_color = 'black'
                    normal_width = 6
                    reverse_width = 5
                    index = -2
                case '1': #0001
                    normal_color = 'black'
                    reverse_color = 'white'
                    normal_width = 5
                    reverse_width = 6
                    index = -1                    
                case '4': #0100
                    normal_color = 'white'
                    reverse_color = 'grey70'
                    normal_width = 6
                    reverse_width = 5
                    index = -2
                case '5': #0101
                    normal_color = 'grey70'
                    reverse_color = 'white'
                    normal_width = 5
                    reverse_width = 6
                    index = -1
                case '8': #1000
                    normal_color = 'white'
                    reverse_color = 'grey60'
                    normal_width = 6
                    reverse_width = 5
                    index = -2
                case '9': #1001
                    normal_color = 'grey60'
                    reverse_color = 'white'
                    normal_width = 5
                    reverse_width = 6
                    index = -1

            self.canvas.itemconfig(self.ids[-2], fill=reverse_color, width = reverse_width)
            self.canvas.itemconfig(self.ids[-1], fill=normal_color, width = normal_width)
            self.canvas.tag_raise(self.ids[index])
        
        self.canvas.after(10, self.update_draw)
            
    def switch_position(self, event):
    
        value = int(self.dataFrame.data['Switch'][self.switch_key], 16)
        if self.type == 'simple':
            value ^= 1
        if self.type == 'double':
            value = (value + 1) % 4
        if self.type == 'scissor':
            value ^= 1
        self.dataFrame.data['Switch'][self.switch_key] = format(value, 'x')

        self.dataFrame.newEvent = True
        self.dataFrame.update_text()
        self.update_draw()    

        self.raise_to_top()

    def convert_coordinates(self,x, y):
        return x + self.width // 2, self.height // 2 - y
    
    def check_for_changes(self):
        current_items = set(self.canvas.find_all())
        if current_items != self.previous_items:
            self.raise_to_top()
        self.previous_items = current_items
        self.canvas.after(10, self.check_for_changes)  # Check for changes every 100 milliseconds

    def raise_to_top(self):
        for id in self.ids:
            self.canvas.tag_raise(id)

def get_netElements(RML):
    network = {}
    coords = {}
    positions = {}
    NetElements =       RML.Infrastructure.Topology.NetElements
    NetRelations =		RML.Infrastructure.Topology.NetRelations
    SwitchesIS =        RML.Infrastructure.FunctionalInfrastructure.SwitchesIS
    LevelCrossingsIS =  RML.Infrastructure.FunctionalInfrastructure.LevelCrossingsIS
    Platforms =         RML.Infrastructure.FunctionalInfrastructure.Platforms
    Borders =           RML.Infrastructure.FunctionalInfrastructure.Borders
    BufferStops =       RML.Infrastructure.FunctionalInfrastructure.BufferStops
    RailJoints =        RML.Infrastructure.FunctionalInfrastructure.TrainDetectionElements
    Crossings =         RML.Infrastructure.FunctionalInfrastructure.Crossings
    SignalsIS =         RML.Infrastructure.FunctionalInfrastructure.SignalsIS
    
    Visualization  =    RML.Infrastructure.InfrastructureVisualizations
    MovableCrossings =  RML.Interlocking.AssetsForIL[0].MovableCrossings

    if NetElements != None:
        for i in NetElements.NetElement:
            if i.Id not in coords.keys():
                if i.AssociatedPositioningSystem != None:
                    if i.AssociatedPositioningSystem[0].IntrinsicCoordinate != None:
                        if len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate) > 1 and i.AssociatedPositioningSystem[0].IntrinsicCoordinate[0].GeometricCoordinate != None:
                            for j in range(len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate)):
                                x = int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].X[:-4])
                                y = -int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].Y[:-4])
                                if i.Id not in coords:
                                    coords[i.Id] = {}
                                    coords[i.Id] = ((x,y),) 
                                else:
                                    coords[i.Id] += ((x,y),) 
    
    for i in coords:
        for j in range(len(coords[i]) - 1):
            if i not in network:
                network[i] = {}
            network[i] |= {f'line{j+1}' : (coords[i][j], coords[i][j + 1])}

        if network[i]['line1'][0][0] < network[i][f'line{len(coords[i]) - 1}'][1][0]:
            network[i] |= {f'Way' : '>'} 
        else:
            network[i] |= {f'Way' : '<'}

    if BufferStops != None:
        for BufferStop in BufferStops[0].BufferStop:
            node = BufferStop.SpotLocation[0].NetElementRef
            bufferStop = BufferStop.Name[0].Name

            if 'BufferStop' not in network[node]:
                network[node] |= {'BufferStop':{}}
            if bufferStop not in network[node]['BufferStop']:
                network[node]['BufferStop'] |= {bufferStop:()}

    if Borders != None:
        for Border in Borders[0].Border:
            if Border.IsOpenEnd == 'true':
                node = Border.SpotLocation[0].NetElementRef
                border = Border.Name[0].Name

                if 'Border' not in network[node]:
                    network[node] |= {'Border':{}}
                if border not in network[node]['Border']:
                    network[node]['Border'] |= {border:()}
                
    if RailJoints != None:
        for RailJoint in RailJoints[0].TrainDetectionElement:
            if RailJoint.Name[0].Name[0] == 'J':
                node = RailJoint.SpotLocation[0].NetElementRef
                border = RailJoint.Name[0].Name

                if 'RailJoint' not in network[node]:
                    network[node] |= {'RailJoint':{}}
                if border not in network[node]['RailJoint']:
                    network[node]['RailJoint'] |= {border:()}

    if LevelCrossingsIS != None:  
        for LevelCrossingIS in LevelCrossingsIS[0].LevelCrossingIS:
            node = LevelCrossingIS.SpotLocation[0].NetElementRef
            levelCrossing = LevelCrossingIS.Name[0].Name

            if 'LevelCrossing' not in network[node]:
                network[node] |= {'LevelCrossing':{}}
            if levelCrossing not in network[node]['LevelCrossing']:
                network[node]['LevelCrossing'] |= {levelCrossing:()}

    if Platforms != None:
    	for Platform in Platforms[0].Platform:
            node = Platform.LinearLocation[0].AssociatedNetElement[0].NetElementRef
            platform = Platform.Name[0].Name

            if 'Platform' not in network[node]:
                network[node] |= {'Platform':{}}
            if platform not in network[node]['Platform']:
                special = ''
                if Platform.LinearLocation[0].AssociatedNetElement[0].LinearCoordinateBegin != None and Platform.LinearLocation[0].AssociatedNetElement[0].LinearCoordinateBegin.LateralSide != None:
                    special = Platform.LinearLocation[0].AssociatedNetElement[0].LinearCoordinateBegin.LateralSide[0]
                network[node]['Platform'] |= {f'{platform}{special}':()}

    if SwitchesIS != None: 
        for SwitchIS in SwitchesIS[0].SwitchIS:
            if (SwitchIS.Type == "ordinarySwitch"):
                
                main = SwitchIS.SpotLocation[0].NetElementRef
                left = SwitchIS.LeftBranch[0].NetRelationRef.split('_')[1].replace(main,'')
                left_radius = SwitchIS.LeftBranch[0].Radius
                right = SwitchIS.RightBranch[0].NetRelationRef.split('_')[1].replace(main,'')

                nodeStart = main
                nodeContinue = left if left_radius == "0" else right
                nodeBranch = right if left_radius == "0"  else left

                if 'Switch' not in network[nodeStart]:
                    network[nodeStart] |= {'Switch':{}}
                if 'Switch_C' not in network[nodeContinue]:
                    network[nodeContinue] |= {'Switch_C':{}}
                if 'Switch_B' not in network[nodeBranch]:
                    network[nodeBranch] |= {'Switch_B':{}}

                network[nodeStart]['Switch'] |= {SwitchIS.Name[0].Name:()}
                network[nodeContinue]['Switch_C'] |= {SwitchIS.Name[0].Name:()} 
                network[nodeBranch]['Switch_B'] |= {SwitchIS.Name[0].Name:()}
            
            if (SwitchIS.Type == "doubleSwitchCrossing"):
                node = SwitchIS.SpotLocation[0].NetElementRef

                straightBranch_A = SwitchIS.StraightBranch[0].NetRelationRef#.split('_')[1]
                straightBranch_B = SwitchIS.StraightBranch[1].NetRelationRef#.split('_')[1]
                turningBranch_A = SwitchIS.TurningBranch[0].NetRelationRef#.split('_')[1]
                turningBranch_B = SwitchIS.TurningBranch[1].NetRelationRef#.split('_')[1]

                straightBranch_1 = straightBranch_A if node in straightBranch_A else straightBranch_B
                turningBranch_1 = turningBranch_A if node in turningBranch_A else turningBranch_B
                straightBranch_2 = straightBranch_B if node in straightBranch_A else straightBranch_B
                turningBranch_2 = turningBranch_B if node in turningBranch_A else turningBranch_B

                nodeStart = node
                nodeInt = straightBranch_1.split('_')[1].split('ne')[1:]
                nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

                #print(f'S:{nodeStart} {nodeEnd}')
                    
                if 'Switch_X' not in network[nodeStart]:
                    network[nodeStart] |= {'Switch_X':{}}
                if 'Switch_X' not in network[nodeEnd]:
                    network[nodeEnd] |= {'Switch_X':{}}
                if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
                    network[nodeStart]['Switch_X'] |= {SwitchIS.Name[0].Name:()}
                if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
                    network[nodeEnd]['Switch_X'] |= {SwitchIS.Name[0].Name:()}

                nodeStart = node
                nodeInt = turningBranch_1.split('_')[1].split('ne')[1:]
                nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

                #print(f'T:{nodeStart} {nodeEnd}')
                    
                if 'Switch_X' not in network[nodeStart]:
                    network[nodeStart] |= {'Switch_X':{}}
                if 'Switch_X' not in network[nodeEnd]:
                    network[nodeEnd] |= {'Switch_X':{}}
                if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
                    network[nodeStart]['Switch_X'] |= {SwitchIS.Name[0].Name:()}
                if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
                    network[nodeEnd]['Switch_X'] |= {SwitchIS.Name[0].Name:()}

                nodeStart = ['ne'+x for x in straightBranch_2.split('_')[1].split('ne')[1:] if x in turningBranch_2.split('_')[1].split('ne')[1:]][0]
                nodeInt = straightBranch_2.split('_')[1].split('ne')[1:]
                nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

                #print(f'S:{nodeStart} {nodeEnd}')
                    
                if 'Switch_X' not in network[nodeStart]:
                    network[nodeStart] |= {'Switch_X':{}}
                if 'Switch_X' not in network[nodeEnd]:
                    network[nodeEnd] |= {'Switch_X':{}}
                if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
                    network[nodeStart]['Switch_X'] |= {SwitchIS.Name[0].Name:()}
                if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
                    network[nodeEnd]['Switch_X'] |= {SwitchIS.Name[0].Name:()}

                nodeStart = ['ne'+x for x in straightBranch_2.split('_')[1].split('ne')[1:] if x in turningBranch_2.split('_')[1].split('ne')[1:]][0]
                nodeInt = turningBranch_2.split('_')[1].split('ne')[1:]
                nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

                #print(f'T:{nodeStart} {nodeEnd}')
                    
                if 'Switch_X' not in network[nodeStart]:
                    network[nodeStart] |= {'Switch_X':{}}
                if 'Switch_X' not in network[nodeEnd]:
                    network[nodeEnd] |= {'Switch_X':{}}
                if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
                    network[nodeStart]['Switch_X'] |= {SwitchIS.Name[0].Name:()}
                if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
                    network[nodeEnd]['Switch_X'] |= {SwitchIS.Name[0].Name:()}
                            
    if Crossings != None:
        for Crossing in Crossings[0].Crossing:
            crossing = Crossing.Name[0].Name

            Net = Crossing.External[0].Ref.split('_')[1].split('ne')
            node1 = 'ne' + Net[1]        
            node2 = 'ne' + Net[2]  

            Net = Crossing.External[1].Ref.split('_')[1].split('ne')
            node3 = 'ne' + Net[1]        
            node4 = 'ne' + Net[2]  

            if 'Crossing' not in network[node1]:
                network[node1] |= {'Crossing':{}}
            if 'Crossing' not in network[node2]:
                network[node2] |= {'Crossing':{}}
            if 'Crossing' not in network[node3]:
                network[node3] |= {'Crossing':{}}
            if 'Crossing' not in network[node4]:
                network[node4] |= {'Crossing':{}}

            if crossing not in network[node1]['Crossing']:
                network[node1]['Crossing'] |= {crossing:()}
            if crossing not in network[node2]['Crossing']:
                network[node2]['Crossing'] |= {crossing:()}
            if crossing not in network[node3]['Crossing']:
                network[node3]['Crossing'] |= {crossing:()}
            if crossing not in network[node4]['Crossing']:
                network[node4]['Crossing'] |= {crossing:()}

            # Extract the 'lineX' coordinates from each netElement
            coordinates = []
            for ne in [node1, node2, node3, node4]:
                for line in network[ne]:
                    if 'line' in line:
                        coordinates.extend(network[ne][line])

            # Find the common coordinate
            common_coordinate = None
            for coordinate in coordinates:
                if coordinates.count(coordinate) == 4:
                    common_coordinate = coordinate
                    break
            #print(f'{crossing} {common_coordinate}')
            positions[crossing] = (int(common_coordinate[0]),int(common_coordinate[1]))

    if SignalsIS != None:
        for SignalIS in SignalsIS.SignalIS:
            node = SignalIS.SpotLocation[0].NetElementRef
            signal = SignalIS.Designator[0].Entry.split(' ')[1]
            direction = SignalIS.SignalConstruction[0].PositionAtTrack[0]
            side = SignalIS.SpotLocation[0].ApplicationDirection[0]
            
            if 'Signal' not in network[node]:
                network[node] |= {'Signal':{}}
            if signal not in network[node]['Signal']:
                network[node]['Signal'] |= {f'{signal}{direction}{side}':()}
    
    if Visualization.Visualization[0].SpotElementProjection != None:
        for i in Visualization.Visualization[0].SpotElementProjection:
            name = i.Name[0].Name
            ref = i.RefersToElement
            if ref.startswith('bus') or name.startswith('Buf') or ref.startswith('oe') or ref.startswith('line') or ref.startswith('tde') or ref.startswith('lcr') or ref.startswith('plf') or ref.startswith('tvd') or ref.startswith('sw') or ref.startswith('dsw') or name.startswith('S'): 
                x_pos = int(float(i.Coordinate[0].X)) if float(i.Coordinate[0].X).is_integer() else float(i.Coordinate[0].X)
                y_pos = -int(float(i.Coordinate[0].Y))  if float(i.Coordinate[0].Y).is_integer() else -float(i.Coordinate[0].Y)
                positions[name] = (int(x_pos),int(y_pos))
                #print(f'-{ref} {name} {positions[name]}')

    for x in positions:
        #print(f'{x} {positions[x]}')
        for node in network:
            if 'BufferStop' in network[node] and x in network[node]['BufferStop']:
                network[node]['BufferStop'] |= {x:positions[x]}
            if 'Border' in network[node] and x in network[node]['Border']:
                network[node]['Border'] |= {x:positions[x]}
            if 'RailJoint' in network[node] and x in network[node]['RailJoint']:
                network[node]['RailJoint'] |= {x:positions[x]}
            if 'LevelCrossing' in network[node] and x in network[node]['LevelCrossing']:
                network[node]['LevelCrossing'] |= {x:positions[x]}
            if 'Platform' in network[node]:
                if x in network[node]['Platform']:
                    network[node]['Platform'] |= {x:positions[x]}
                if x+'l' in network[node]['Platform']:
                    network[node]['Platform'] |= {f'{x}l':positions[x]}
                if x+'r' in network[node]['Platform']:
                    network[node]['Platform'] |= {f'{x}r':positions[x]}
            if 'Switch' in network[node] and x in network[node]['Switch']:
                network[node]['Switch'] |= {x:positions[x]}
            if 'Switch_B' in network[node] and x in network[node]['Switch_B']:
                network[node]['Switch_B'] |= {x:positions[x]}
            if 'Switch_C' in network[node] and x in network[node]['Switch_C']:
                network[node]['Switch_C'] |= {x:positions[x]}
            if 'Switch_X' in network[node] and x in network[node]['Switch_X']:
                network[node]['Switch_X'] |= {x:positions[x]}
            if 'Crossing' in network[node] and x in network[node]['Crossing']:
                network[node]['Crossing'] |= {x:positions[x]}
            if 'Signal' in network[node]:
                way = network[node]['Way']

                if x+'ln' in network[node]['Signal'] or x+'lr' in network[node]['Signal'] or x+'rn' in network[node]['Signal'] or x+'rr' in network[node]['Signal']:
                    min_distance = float('inf')
                    min_line = None

                    for line_name, line in network[node].items():
                        if line_name.startswith('line'):
                            (x1, y1), (x2, y2) = line
                            (x0, y0) = positions[x]
                            dx, dy = x2 - x1, y2 - y1
                            t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
                            if t < 0:
                                t = 0
                            elif t > 1:
                                t = 1
                            projected = x1 + t * dx, y1 + t * dy
                            dist = math.hypot(x0 - projected[0], y0 - projected[1])
                            if dist < min_distance:
                                min_distance = dist
                                min_line = line_name
 
                    #print(f'//{x} {node} {min_line}')

                    if min_line != None:
                        if network[node][min_line][0][1] == network[node][min_line][1][1]:
                            position = (positions[x][0],network[node][min_line][0][1])
                        else:
                            position = ((network[node][min_line][0][0] + network[node][min_line][1][0]) / 2, (network[node][min_line][0][1] + network[node][min_line][1][1]) / 2) #positions[x]

                        #print(f'*{x} {positions[x]} {node} {min_line} {way} {position}')

                    if x+'ln' in network[node]['Signal']:
                        network[node]['Signal'] |= {f'{x}ln':position}
                    if x+'lr' in network[node]['Signal']:
                        network[node]['Signal'] |= {f'{x}lr':position}
                    if x+'rn' in network[node]['Signal']:
                        network[node]['Signal'] |= {f'{x}rn':position}
                    if x+'rr' in network[node]['Signal']:
                        network[node]['Signal'] |= {f'{x}rr':position}
                    
    return network

def create_canvas(window, width, height,bg_color):
    return tk.Canvas(window, width=width, height=height, bg=bg_color)

def calculate_coordinate(core_point, line_points, distance):
    # Calculate the direction vector of the line
    dx = line_points[1][0] - line_points[0][0]
    dy = line_points[1][1] - line_points[0][1]
    
    # Calculate the magnitude of the direction vector
    magnitude = (dx**2 + dy**2)**0.5
    
    # Normalize the direction vector
    normalized_dx = dx / magnitude
    normalized_dy = dy / magnitude
    
    # Determine the direction from the core point to the other point on the line
    if core_point == line_points[0]:
        # Calculate the new coordinate
        new_x = core_point[0] + distance * normalized_dx
        new_y = core_point[1] + distance * normalized_dy
    else:
        # Calculate the new coordinate
        new_x = core_point[0] - distance * normalized_dx
        new_y = core_point[1] - distance * normalized_dy
    
    #return (int(new_x), int(new_y))
    return (new_x, new_y)

def create_switches_pos(netElements):
    switches_pos = {}

    for ne in netElements:
        if 'Switch' in netElements[ne]:
            for switch in netElements[ne]['Switch']:
                core = netElements[ne]['Switch'][switch]
                switches_pos[switch] = [core]
                #print(f'{ne} {switch}')
                line_key = next(key for key in netElements[ne] if key.startswith('line') and tuple(map(int, core)) in netElements[ne][key])
                line = netElements[ne][line_key]
                point_on_line = calculate_coordinate(core, line, 50)

                #print(f'{switch} -|- {core} -|- {ne} {line_key} {line} | {point_on_line}')

                switches_pos[switch].append(point_on_line)

    for ne in netElements:
        if 'Switch_B' in netElements[ne]:
            for switch_b in netElements[ne]['Switch_B']:
                core = switches_pos[switch_b][0]
                line_key = next(key for key in netElements[ne] if key.startswith('line') and tuple(map(int, core)) in netElements[ne][key])
                line = netElements[ne][line_key]
                point_on_line = calculate_coordinate(core, line, 50)

                #print(f'{switch_b} -|- {core} -|- {ne} {line_key} {line} | {point_on_line}')

                switches_pos[switch_b].append(point_on_line)

    for ne in netElements:
        if 'Switch_C' in netElements[ne]:
            for switch_c in netElements[ne]['Switch_C']:
                core = switches_pos[switch_c][0]
                line_key = next(key for key in netElements[ne] if key.startswith('line') and tuple(map(int, core)) in netElements[ne][key])
                line = netElements[ne][line_key]
                point_on_line = calculate_coordinate(core, line, 50)

                #print(f'{switch_c} -|- {core} -|- {ne} {line_key} {line} | {point_on_line}')

                switches_pos[switch_c].append(point_on_line)

    for ne in netElements:
        if 'Switch_X' in netElements[ne]:
            for switch_x in netElements[ne]['Switch_X']:

                if switch_x not in switches_pos:
                    core = netElements[ne]['Switch_X'][switch_x]
                    switches_pos[switch_x] = [core]
                else:
                    core = switches_pos[switch_x][0]

                line_key = next(key for key in netElements[ne] if key.startswith('line') and tuple(map(int, core)) in netElements[ne][key])
                line = netElements[ne][line_key]
                point_on_line = calculate_coordinate(core, line, 50)

                #print(f'{switch_x} -|- {core} -|- {ne} {line_key} {line} | {point_on_line}')
                
                switches_pos[switch_x].append(point_on_line)
                #print(f'{switch_x} {switches_pos[switch_x]}')

    for ne in netElements:
        if 'Crossing' in netElements[ne]:
            for crossing in netElements[ne]['Crossing']:

                if crossing not in switches_pos:
                    core = netElements[ne]['Crossing'][crossing]
                    switches_pos[crossing] = [core]
                else:
                    core = switches_pos[crossing][0]

                line_key = next(key for key in netElements[ne] if key.startswith('line') and tuple(map(int, core)) in netElements[ne][key])
                line = netElements[ne][line_key]
                point_on_line = calculate_coordinate(core, line, 50)

                #print(f'{switch_x} -|- {core} -|- {ne} {line_key} {line} | {point_on_line}')
                
                switches_pos[crossing].append(point_on_line)
                if len(switches_pos[crossing]) == 5:
                    switches_pos[crossing][0] = (0,0)

    return switches_pos

def draw_lines(canvas, dataFrame,network, switches_pos,width, height, netElement,switches,signal_routes,signals):
    def convert_coordinates(x, y):
        return x + width // 2, height // 2 - y
    net_elements = {}
    levelCrossings = {}
    
    for key, value in network[netElement].items():
        if key.startswith('line'):
            x1y1, x2y2 = value
            net_element = NetElement(canvas,dataFrame, *convert_coordinates(*x1y1), *convert_coordinates(*x2y2), net_elements, netElement)
            net_elements[key] = net_element
        if key.startswith('BufferStop'):
            for i in value:
                x,y = value[i]
                line_xs = [coord[0] for key, value in network[netElement].items() if key.startswith('line') for coord in value]
                #print(f'---{i} {line_xs} | {int(x)}')
                direction = '>' if all(int(x) >= line_x for line_x in line_xs) else '<'

                #print(f'{i} {x} {line_xs} {direction}')

                buffer_stop = BufferStop(canvas, *convert_coordinates(x, y), direction)
                net_elements[key] = buffer_stop
        if key.startswith('Border'):
            for i in value:
                x,y = value[i]
                line_xs = [coord[0] for key, value in network[netElement].items() if key.startswith('line') for coord in value]
                direction = '>' if all(x >= line_x for line_x in line_xs) else '<'
                #print(f'{i} {x} {line_xs} {direction}')

                border = Border(canvas, *convert_coordinates(x, y), direction)
                net_elements[key] = border
        if key.startswith('RailJoint'):
            for i in value:
                x,y = value[i]
                railJoint = RailJoint(canvas, *convert_coordinates(x, y))
                net_elements[key] = railJoint
        if key.startswith('Platform'):
            for i in value:
                x,y = value[i]
                #print(key,value,i)
                direction = network[netElement]['Way']

                if i[-1] == 'r':
                    side = 'right'
                else:
                    side = 'left'

                if direction == '>' and side == 'left':
                    alignment = 'top'
                if direction == '>' and side == 'right':
                    alignment = 'bottom'
                if direction == '<' and side == 'left':
                    alignment = 'bottom'
                if direction == '<' and side == 'right':
                    alignment = 'top'

                platform = Platform(canvas, *convert_coordinates(x, y), alignment)
                net_elements[key] = platform
        if key.startswith('LevelCrossing'):
            for i in value:
                x,y = value[i]
                levelCrossing = LevelCrossing(canvas,dataFrame, *convert_coordinates(x, y), levelCrossings,i)
                levelCrossings[key] = levelCrossing       
        if key.startswith('Signal'):
            for i in value:
                x,y = value[i]
                name = i[:-2]
                #print(f'---{i} {x} {y}')
                way = network[netElement]['Way']

                min_distance = float('inf')
                min_line = None
                for line_name, line in network[netElement].items():
                    if line_name.startswith('line'):
                        (x1, y1), (x2, y2) = line
                        (x0, y0) = (x,y)
                        dx, dy = x2 - x1, y2 - y1
                        t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
                        if t < 0:
                            t = 0
                        elif t > 1:
                            t = 1
                        projected = x1 + t * dx, y1 + t * dy
                        dist = math.hypot(x0 - projected[0], y0 - projected[1])
                        if dist < min_distance:
                            min_distance = dist
                            min_line = line_name

                net_coordinate = None
                if min_line != None:
                    if network[netElement][min_line][0][1] != network[netElement][min_line][1][1]:
                        net_coordinate = network[netElement][min_line]

                next_signals = None
                if name in signal_routes:
                    next_signals = signal_routes[name]
                    #print(next_signals)
                signals[name] = Signals(canvas,dataFrame, *convert_coordinates(x, y),i,way,net_coordinate, other_signals = next_signals,signals = signals)
        if key.startswith('Switch'):
            for i in value:
                if i in switches_pos and i not in switches:
                    #print(f'----{key} {i}')
                    x,y = value[i]
                    switches[i] = Switch(canvas,dataFrame,width,height,switches_pos,i,switches)
        if key.startswith('Crossing'):
            for i in value:
                if i in switches_pos and i not in switches:
                    #print(f'----{key} {i}')
                    x,y = value[i]
                    switches[i] = Switch(canvas,dataFrame,width,height,switches_pos,i,switches)
    return net_elements

def bind_events(canvas, lines):
    def on_button_press(event):
        canvas.scan_mark(event.x, event.y)

    def on_drag(event):
        canvas.scan_dragto(event.x, event.y, gain=1)

    def on_zoom(event):
        factor = 1.0 + event.delta * 0.001
        canvas.scale("all", event.x, event.y, factor, factor)

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<Shift-B1-Motion>", on_drag)
    canvas.bind("<MouseWheel>", on_zoom)

def split_data(input_string, n_netElements, n_routes, n_signals, n_levelCrossings, n_switches, n_doubleSwitch, n_scissorCrossings):
    # Remove the angle brackets from the input string
    data_string = input_string#[1:-1]

    # Calculate the starting index for each variable
    start_routes = n_netElements
    start_signals = start_routes + n_routes
    start_levelCrossings = start_signals + n_signals
    start_switches = start_levelCrossings + n_levelCrossings
    start_doubleSwitch = start_switches + n_switches
    start_scissorCrossings = start_doubleSwitch + n_doubleSwitch

    # Split the data string into the variables
    data_tracks = data_string[:start_routes]
    data_routes = data_string[start_routes:start_signals]
    data_signals = data_string[start_signals:start_levelCrossings]
    data_levelCrossings = data_string[start_levelCrossings:start_switches]
    data_switches = data_string[start_switches:]
    #data_switches = data_string[start_switches:start_doubleSwitch]
    #data_doubleSwitch = data_string[start_doubleSwitch:start_scissorCrossings]
    #data_scissorCrossings = data_string[start_scissorCrossings:]

    return data_tracks, data_routes, data_signals, data_levelCrossings, data_switches#, data_doubleSwitch, data_scissorCrossings

def merge_data_from_gui(dataFrame, new_data):
    # Example: Merging new data from the GUI into dataFrame
    # This is a simple example, you might need a more complex merging logic
    #dataFrame.data.update(new_data)
    return

def update_dataFrame(dataFrame, n_netElements, n_routes, n_signals, n_levelCrossings, n_switches, n_doubleSwitch, n_scissorCrossings,data_tracks, data_routes, data_signals, data_levelCrossings, data_switches):

    if n_netElements > 0:
        for tck_index, tck_key in enumerate(dataFrame.data['Occupation'].keys()):
            dataFrame.data['Occupation'][tck_key] = str(data_tracks[tck_index])

    if n_routes > 0:
        for rt_index, rt_key in enumerate(dataFrame.data['Routes'].keys()):
            dataFrame.data['Routes'][rt_key] = str(data_routes[rt_index])

    if n_signals > 0:
        for sig_index, sig_key in enumerate(dataFrame.data['Signal'].keys()):
            dataFrame.data['Signal'][sig_key] = str(data_signals[sig_index])

    if n_levelCrossings > 0:
        for lc_index, lc_key in enumerate(dataFrame.data['LevelCrossing'].keys()):
            dataFrame.data['LevelCrossing'][lc_key] = str(data_levelCrossings[lc_index])

    if n_switches > 0:
        for sw_index, sw_key in enumerate(dataFrame.data['Switch'].keys()):
            dataFrame.data['Switch'][sw_key] = str(data_switches[sw_index])

 # Function to handle GUI updates, enqueueing them

def handle_gui_update(new_data):
    gui_queue.put(new_data)

def read_and_write_data(window, serialComm, dataFrame, n_netElements, n_routes, n_signals, n_levelCrossings, n_switches, n_doubleSwitch, n_scissorCrossings):

    # Check if there's an update from the GUI
    if not gui_queue.empty():
        new_data = gui_queue.get()
        # Update dataFrame with new GUI data
        merge_data_from_gui(dataFrame, new_data)

    dataFrame.dataReceived = serialComm.read()
    if dataFrame.dataReceived is not None:           
        print(f"<<< {dataFrame.dataReceived}")
        
         # Assuming split_data function processes received data
        data_tracks, data_routes, data_signals, data_levelCrossings, data_switches = split_data(dataFrame.dataReceived, n_netElements, n_routes, n_signals, n_levelCrossings, n_switches, n_doubleSwitch, n_scissorCrossings)

         # Update dataFrame with received data
        update_dataFrame(dataFrame, n_netElements, n_routes, n_signals, n_levelCrossings, n_switches, n_doubleSwitch, n_scissorCrossings,data_tracks, data_routes, data_signals, data_levelCrossings, data_switches)
                
        dataFrame.update_text()
    
        #print(f'>   {dataFrame.dataSent[1:-1]}\n<   {dataFrame.dataReceived}')
        if dataFrame.dataSent[1:-1] != dataFrame.dataReceived:
            print(f'X>> {dataFrame.dataSent[1:-1]}')            
            serialComm.write(dataFrame.dataSent)

    else:
        print(f'\n>   {dataFrame.dataSent[1:-1]}')
        serialComm.write(dataFrame.dataSent)

    # Schedule the function to be called again after 100ms
    window.after(100, read_and_write_data, window, serialComm, dataFrame, n_netElements, n_routes, n_signals, n_levelCrossings, n_switches, n_doubleSwitch, n_scissorCrossings)

def AGG(RML,routes,parameters,test = False):
    print("#"*20+" Starting Automatic GUI Generator "+"#"*20)
    print("Reading railML object")
    #return
    netElements = get_netElements(RML)

    for netElement in netElements:
        print(f'{netElement} {netElements[netElement]}')

    signal_routes = {}
    for route in routes:
        #print(f'R{route} {routes[route]}')
        start = 'S'+str(routes[route]['Start'][1:])
        end = 'S'+str(routes[route]['End'][1:])
        if start not in signal_routes:
            signal_routes[start] = {}
        signal_routes[start] |= {end:f'R{route}'}

    #for signal in signal_routes:
    #    print(f'{signal} {signal_routes[signal]}')
    
    switches_pos = create_switches_pos(netElements)

    #for switch in switches_pos:
    #    print(f'{switch} {switches_pos[switch]}')

    print("Generating GUI layout")
    
    window = tk.Tk()
    width, height = 1200, 800
    
    bg_color = "white"  # Define the background color

    canvas = create_canvas(window, width, height,bg_color)
    canvas.pack(fill='both', expand=True)

    switches = {}
    signals = {}

    dataFrame = DataFrame(window,canvas, netElements, routes, width, height)

    for netElement in netElements:
        lines_plot = draw_lines(canvas, dataFrame,netElements, switches_pos, width, height,netElement,switches,signal_routes,signals)
        bind_events(canvas, lines_plot)

    # Update the window to make sure all widgets are drawn before we get the bounding box
    window.update_idletasks()
    
    # Get the bounding box of all items on the canvas
    bbox = canvas.bbox("all")

    # Calculate the center of the bounding box
    center_x = (bbox[2] + bbox[0]) // 2
    center_y = (bbox[3] + bbox[1]) // 2

    # Calculate the distance to move to center the bounding box
    dx = width // 2 - center_x
    dy = height // 2 - center_y

    # Move all items on the canvas to center the bounding box
    canvas.move("all", dx, dy)

    # Update the window again to reflect the changes
    window.update_idletasks()

    # Add a protocol for when the window is closed
    window.protocol("WM_DELETE_WINDOW", window.destroy)

    # Create an instance of SerialComm
    serialComm = SerialComm('COM3')  # Replace 'COMx' with your actual COM port

    print(parameters)

    N                       = parameters[0]
    M                       = parameters[1]
    n_netElements           = parameters[2]
    n_routes                = parameters[3]
    n_signals               = parameters[4]
    n_levelCrossings        = parameters[5]
    n_switches              = parameters[6]
    n_doubleSwitch          = parameters[7]
    n_scissorCrossings      = parameters[8]

    dataFrame.newEvent = True
    # Schedule the function to be called after 100ms
    window.after(500, read_and_write_data, window, serialComm, dataFrame, n_netElements, n_routes, n_signals, n_levelCrossings, n_switches, n_doubleSwitch, n_scissorCrossings)

    # Main loop for tkinter
    window.mainloop()