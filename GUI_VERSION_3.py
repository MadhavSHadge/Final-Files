import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QGridLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPalette
import serial
import datetime
import time

# Define the file path for saving motor settings
file_path = 'motor_settings.txt'

class MotorControlGUI(QMainWindow):
    def __init__(self, motor_control):
        super().__init__()
        self.motor_control = motor_control
        self.initUI()
        
        #initialize serial communication
        self.init_serial()
        
    def init_serial(self):
        self.serial_port = serial.Serial('COM3', 9600, timeout=1)  # Adjust COM port as needed

    def send_serial_command(self, command):
        self.serial_port.write(command.encode())

    def initUI(self):
        self.setWindowTitle('Arduino Motor Control')
        self.setGeometry(100, 100, 800, 600)
        
        # Set dark mode theme
        self.setDarkMode()
    
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()  # Use QHBoxLayout for three-column layout
        central_widget.setLayout(main_layout)
    
        # First Column
        first_column_layout = QVBoxLayout()
        main_layout.addLayout(first_column_layout)
    
        # Set Pulses per Revolution
        pulses_group = QGroupBox('Set Pulses per Revolution')
        pulses_layout = QVBoxLayout()
        pulses_group.setLayout(pulses_layout)
    
        self.pulses_entry = QLineEdit()
        pulses_layout.addWidget(self.pulses_entry)
    
        self.submit_pulses_button = QPushButton('Submit Pulses')
        self.submit_pulses_button.clicked.connect(self.submit_pulses)
        pulses_layout.addWidget(self.submit_pulses_button)
    
        first_column_layout.addWidget(pulses_group)
    
        # Set Gear Ratio
        gear_ratio_group = QGroupBox('Set Gear Ratio')
        gear_ratio_layout = QVBoxLayout()
        gear_ratio_group.setLayout(gear_ratio_layout)
    
        self.gear_ratio_entry = QLineEdit()
        gear_ratio_layout.addWidget(self.gear_ratio_entry)
    
        self.submit_gear_ratio_button = QPushButton('Submit Gear Ratio')
        self.submit_gear_ratio_button.clicked.connect(self.submit_gear_ratio)
        gear_ratio_layout.addWidget(self.submit_gear_ratio_button)
    
        first_column_layout.addWidget(gear_ratio_group)
    
        # Set Antenna Angle
        pulse_group = QGroupBox('Set Antenna Angle')
        pulse_layout = QGridLayout()
        pulse_group.setLayout(pulse_layout)
    
        pulse_label = QLabel('Enter Angle In Degrees:')
        pulse_layout.addWidget(pulse_label, 0, 0)
    
        self.pulse_entry = QLineEdit()
        pulse_layout.addWidget(self.pulse_entry, 0, 1)
    
        first_column_layout.addWidget(pulse_group)
    
        # Direction Controls
        direction_group = QGroupBox('Direction Controls')
        direction_layout = QVBoxLayout()
        direction_group.setLayout(direction_layout)
    
        self.forward_button = QPushButton('Clockwise')
        self.forward_button.clicked.connect(self.forward)
        direction_layout.addWidget(self.forward_button)
    
        self.backward_button = QPushButton('Anticlockwise')
        self.backward_button.clicked.connect(self.backward)
        direction_layout.addWidget(self.backward_button)
    
        self.direction_button = QPushButton('Direction Find')
        self.direction_button.clicked.connect(self.direction_count)
        direction_layout.addWidget(self.direction_button)
    
        first_column_layout.addWidget(direction_group)
    
        # Second Column
        second_column_layout = QVBoxLayout()
        main_layout.addLayout(second_column_layout)
    
        # Set Clock For Rotation
        timer_group = QGroupBox('Set Clock For Rotation')
        timer_layout = QGridLayout()
        timer_group.setLayout(timer_layout)
    
        self.hours_entry = QLineEdit('00')
        timer_layout.addWidget(self.hours_entry, 0, 0)
    
        self.minutes_entry = QLineEdit('00')
        timer_layout.addWidget(self.minutes_entry, 0, 1)
    
        self.seconds_entry = QLineEdit('00')
        timer_layout.addWidget(self.seconds_entry, 0, 2)
    
        start_stop_layout = QHBoxLayout()
        timer_layout.addLayout(start_stop_layout, 1, 0, 1, 3)
    
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_timer)
        start_stop_layout.addWidget(self.start_button)
    
        self.stop_button_timer = QPushButton('Stop')
        self.stop_button_timer.clicked.connect(self.stop_timer)
        start_stop_layout.addWidget(self.stop_button_timer)
    
        second_column_layout.addWidget(timer_group)
    
        # Speed Controls
        motor_controls_group = QGroupBox('Speed Controls')
        motor_controls_layout = QVBoxLayout()
        motor_controls_group.setLayout(motor_controls_layout)
    
        self.speed_label = QLabel('Calculated Speed (PWM 0-255):')
        motor_controls_layout.addWidget(self.speed_label)
    
        self.calculated_speed_display = QLabel('N/A')
        motor_controls_layout.addWidget(self.calculated_speed_display)
    
        second_column_layout.addWidget(motor_controls_group)
    
        # Encoder Value
        encoder_group = QGroupBox('Encoder Value')
        encoder_layout = QVBoxLayout()
        encoder_group.setLayout(encoder_layout)
    
        self.encoder_value_label = QLabel('Current Encoder Value: N/A')
        encoder_layout.addWidget(self.encoder_value_label)
    
        self.read_encoder_button = QPushButton('Read Encoder Value')
        self.read_encoder_button.clicked.connect(self.read_encoder)
        encoder_layout.addWidget(self.read_encoder_button)
    
        second_column_layout.addWidget(encoder_group)
    
        # Third Column
        third_column_layout = QVBoxLayout()
        main_layout.addLayout(third_column_layout)
    
        # Submit and Reset Parameters
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)
    
        self.submit_button = QPushButton('Submit Parameters')
        self.submit_button.clicked.connect(self.submit_parameters)
        bottom_layout.addWidget(self.submit_button)
    
        self.reset_button = QPushButton('Reset Parameters')
        self.reset_button.clicked.connect(self.reset_all)
        bottom_layout.addWidget(self.reset_button)
    
        self.reset_antenna_button = QPushButton('Reset Antenna Position')
        self.reset_antenna_button.clicked.connect(self.reset_antenna_position)
        bottom_layout.addWidget(self.reset_antenna_button)

        # Spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        # Initialize settings from file
        self.read_motor_settings()

    def reset_antenna_position(self):
        # Implement logic to reset antenna position
        self.pulse_entry.clear()  # Clear the angle entry

        QMessageBox.information(self, "Reset Antenna Position", "Antenna position has been reset.")
        self.motor_control.write_log("Antenna position reset")

    def read_motor_settings(self):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    self.pulse_entry.setText(lines[1].strip())

    def start_timer(self):
        try:
            total_time = int(self.hours_entry.text()) * 3600 + int(self.minutes_entry.text()) * 60 + int(self.seconds_entry.text())
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Please enter valid integers for hours, minutes, and seconds.")
            return

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        # Calculate PWM based on the given time
        rpm = 10  # Motor's RPM
        rotations_per_second = rpm / 60
        pulses_per_rotation = int(self.pulses_entry.text()) if self.pulses_entry.text().isdigit() else 360  # Default to 360 if not specified
        required_rotations = total_time / 60 / 60 * rpm
        required_pulses = required_rotations * pulses_per_rotation

        # Convert pulses to PWM (0-255)
        pwm_value = min(max(int((required_pulses / pulses_per_rotation) * 255), 0), 255)
        self.calculated_speed_display.setText(str(pwm_value))

        # Log to file
        self.motor_control.write_log(f"Timer set: {total_time} seconds, PWM calculated: {pwm_value}")

    def stop_timer(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.motor_control.stop_motor()
        QMessageBox.information(self, "Timer Stopped", "The timer has been stopped and motor has been stopped.")
        self.motor_control.write_log("Timer stopped")

    @pyqtSlot()
    def update_timer(self):
        total_time = int(self.hours_entry.text()) * 3600 + int(self.minutes_entry.text()) * 60 + int(self.seconds_entry.text())
        total_time -= 1

        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        seconds = total_time % 60

        self.hours_entry.setText(f"{hours:02}")
        self.minutes_entry.setText(f"{minutes:02}")
        self.seconds_entry.setText(f"{seconds:02}")

        if total_time <= 0:
            self.timer.stop()
            self.motor_control.stop_motor()
            QMessageBox.information(self, "Timer Finished", "The timer has finished and motor has been stopped.")
            self.motor_control.write_log("Timer finished")

    def submit_pulses(self):
        pulses_per_revolution = self.pulses_entry.text()
        try:
            pulses_per_revolution = int(pulses_per_revolution)
            if pulses_per_revolution <= 0:
                raise ValueError("Pulses per revolution must be a positive integer.")

            self.send_serial_command(f"P{pulses_per_revolution}")
            self.motor_control.set_pulses_per_revolution(pulses_per_revolution)
            self.motor_control.write_motor_settings()
            QMessageBox.information(self, "Pulses Set", f"Pulses per revolution set to {pulses_per_revolution}.")
            self.motor_control.write_log(f"Pulses per revolution set: {pulses_per_revolution}")

        except ValueError as e:
            QMessageBox.critical(self, "Invalid Input", str(e))

    def submit_parameters(self):
        angle = self.pulse_entry.text()
        self.motor_control.send_command(f"A{angle}")

        # Handle pulses per revolution separately if needed
        pulses_per_revolution = self.pulses_entry.text()
        if pulses_per_revolution.isdigit():
            self.motor_control.set_pulses_per_revolution(int(pulses_per_revolution))

        self.motor_control.write_motor_settings()
        QMessageBox.information(self, "Parameters Set", "All parameters have been submitted and set.")
        self.motor_control.write_log(f"Angle set: {angle}, Pulses per revolution set: {pulses_per_revolution}")

    def forward(self):
        self.motor_control.forward()
        self.motor_control.send_command('F')  # Send command 'F' for forward
        QMessageBox.information(self, "Direction Set", "Direction set to Clockwise")
        self.motor_control.write_log("Direction set to Clockwise")

    def backward(self):
        self.motor_control.backward()
        self.motor_control.send_command('B')
        QMessageBox.information(self, "Direction Set", "Direction set to Anticlockwise")
        self.motor_control.write_log("Direction set to Anticlockwise")

    def direction_count(self):
        self.motor_control.direction_count()
        self.motor_control.send_command('D')
        QMessageBox.information(self, "Direction Count", "Direction count set")
        self.motor_control.write_log("Direction count set")

    def read_encoder(self):
        self.motor_control.read_encoder()
        encoder_value = self.motor_control.ser.readline().decode().strip()
        self.encoder_value_label.setText(f"Current Encoder Value: {encoder_value}")
        self.motor_control.write_log(f"Encoder value read: {encoder_value}")

    def reset_all(self):
        self.pulse_entry.clear()
        self.hours_entry.setText('00')
        self.minutes_entry.setText('00')
        self.seconds_entry.setText('00')
        self.calculated_speed_display.setText('N/A')
        self.encoder_value_label.setText('Current Encoder Value: N/A')
        self.motor_control.stop_motor()
        QMessageBox.information(self, "Reset", "All settings have been reset.")
        self.motor_control.write_log("All settings reset")

    def setDarkMode(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def submit_gear_ratio(self):
        gear_ratio_text = self.gear_ratio_entry.text().strip()
        try:
            gear_ratio = float(gear_ratio_text)
            if gear_ratio <= 0:
                raise ValueError("Gear ratio must be a positive number.")

            self.send_serial_command(f"G{gear_ratio}")
            QMessageBox.information(self, "Gear Ratio Set", f"Gear ratio set to {gear_ratio}.")
            self.motor_control.write_log(f"Gear ratio set: {gear_ratio}")

        except ValueError as e:
            QMessageBox.critical(self, "Invalid Input", str(e))

    def closeEvent(self, event):
        self.serial_port.close()
        super().closeEvent(event)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    motor_control = None  # Replace with your motor control instance
    window = MotorControlGUI(motor_control)
    window.show()
    sys.exit(app.exec_())
