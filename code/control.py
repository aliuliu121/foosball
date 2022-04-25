import serial
import time
import parse

class TableController:
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyACM0", 250000)
        time.sleep(1)
        self.home_table()
        self.setup_mode()
    
    def play(self, ball_position):
        # calculate dist to nearest player
        # if dist < threshold, launch
        # else move closest pole toward direction of ball
        # make sure command has finished executing before returning
        # receiving ok doesn't mean command is done, just adknowledge
        dist_from_y_pole = 59 - ball_position[0]
        dist_from_x_pole = 246 - ball_position[0]

        curr_state = self.get_machine_state()
        # print(ball_position)
        # print(curr_state)
        
        if abs(dist_from_x_pole) < abs(dist_from_y_pole):
            pole_name = 'X'
            pole_pos = float(curr_state[0])
            dist_from_pole = dist_from_x_pole
        else:
            pole_name = 'Y'
            pole_pos = float(curr_state[1])
            dist_from_pole = dist_from_y_pole

        desired_pole_placement = (ball_position[1] % 95)
        if desired_pole_placement < 15 and ball_position[1] < 95:
            desired_pole_placement = 0
        elif desired_pole_placement > 80 and ball_position[1] > 190:
            desired_pole_placement = 92
        desired_displacement = desired_pole_placement - pole_pos

        if abs(desired_displacement) >= 2:
            if abs(desired_displacement) < 3:
                self.move_pole(pole_name, desired_displacement)
            else:
                self.move_pole(pole_name, desired_displacement * 0.1)
        else:
            if dist_from_pole > -40 and dist_from_pole < 0:
                self.rotate_forward(pole_name)
            elif dist_from_pole >= 0 and dist_from_pole < 26:
                self.grab_ball_behind(pole_name, pole_pos)

    def get_machine_state(self):
        x = -1
        y = -1

        self.ser.write("M114\r\n".encode())
        while True:
            line = self.ser.readline()
            decoded = line.decode()
            format = 'X:{} Y:{} Z:{} E:{} Count X:{} Y:{} Z:{}\n'
            parsed_values = parse.parse(format, decoded)
            if parsed_values is not None:
                x = float(parsed_values[0])
                y = float(parsed_values[1])
                break
        self.ser.reset_input_buffer()
        return (x,y)

    def rotate_forward(self, pole):
        if pole == 'X':
            self.ser.write("T01\r\n".encode())
        else:
            self.ser.write("T0\r\n".encode())
        self.ser.write("G0 E6.5\r\n".encode())
        time.sleep(0.1)
        self.ser.write("G0 E-6.5\r\n".encode())

    def grab_ball_behind(self, pole, pole_position):
        if pole == 'X':
            self.ser.write("T01\r\n".encode())
        else:
            self.ser.write("T0\r\n".encode())
        
        if pole_position < 42.5:
            movement = 30
        else:
            movement = -30

        command1 = "G0 {}{} F8000\r\n".format(pole, movement)
        self.ser.write(command1.encode())
        time.sleep(0.1)
        self.ser.write("G0 E-8\r\n".encode())
        time.sleep(0.1)
        command2 = "G0 {}{} F8000\r\n".format(pole, -1*movement)
        self.ser.write(command2.encode())
        time.sleep(0.1)
        self.ser.write("G0 E8\r\n".encode())
    
    def rotate_backward(self, pole):
        if pole == 'X':
            self.ser.write("T01\r\n".encode())
        else:
            self.ser.write("T0\r\n".encode())
        self.ser.write("G0 E-6.5\r\n".encode())
        time.sleep(0.1)
        self.ser.write("G0 E6.5\r\n".encode())

    def move_pole(self, pole, amount):
        command = "G0 {}{} F8000\r\n".format(pole, amount)
        self.ser.write(command.encode())
        #time.sleep(0.05)
    
    def home_table(self):
        self.ser.write("G28 XY\r\n".encode())
        time.sleep(4)
        self.ser.reset_input_buffer()

    def setup_mode(self):
        self.ser.write("G91\r\n".encode())
        time.sleep(1)
        self.ser.reset_input_buffer()

    def close(self):
        self.ser.close()

