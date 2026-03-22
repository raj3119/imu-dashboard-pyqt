import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import csv
from datetime import datetime
from simulator import get_imu_data


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMU Dashboard")

        self.log_data = []
        self.time_step = 0  

        self.layout = QVBoxLayout()

            # Acceleration Plot 
        self.accel_plot = pg.PlotWidget(title="Acceleration (m/s²)")
        self.accel_plot.setLabel('left', 'Acceleration (m/s²)')
        self.accel_plot.setLabel('bottom', 'Time')

        # Add grid
        self.accel_plot.showGrid(x=True, y=True)

        # position
        accel_legend = self.accel_plot.addLegend(offset=(10, 7))

        self.accel_x = self.accel_plot.plot(pen='r', name="X")
        self.accel_y = self.accel_plot.plot(pen='g', name="Y")
        self.accel_z = self.accel_plot.plot(pen='b', name="Z")

        self.layout.addWidget(self.accel_plot)


        #  Gyroscope Plot 
        self.gyro_plot = pg.PlotWidget(title="Gyroscope (°/s)")
        self.gyro_plot.setLabel('left', 'Angular Velocity (°/s)')
        self.gyro_plot.setLabel('bottom', 'Time')

        #  Add grid
        self.gyro_plot.showGrid(x=True, y=True)

        # position
        gyro_legend = self.gyro_plot.addLegend(offset=(10, 7))

        self.gyro_x = self.gyro_plot.plot(pen='r', name="X")
        self.gyro_y = self.gyro_plot.plot(pen='g', name="Y")
        self.gyro_z = self.gyro_plot.plot(pen='b', name="Z")

        self.layout.addWidget(self.gyro_plot)

        # Orientation Panel
        self.orientation_box = QGroupBox("Orientation (Degrees)")
        self.orientation_layout = QVBoxLayout()

        self.roll_label = QLabel("Roll: 0°")
        self.pitch_label = QLabel("Pitch: 0°")
        self.yaw_label = QLabel("Yaw: 0°")

        self.orientation_layout.addWidget(self.roll_label)
        self.orientation_layout.addWidget(self.pitch_label)
        self.orientation_layout.addWidget(self.yaw_label)

        self.orientation_box.setLayout(self.orientation_layout)
        self.layout.addWidget(self.orientation_box)

        # Status 
        self.status_label = QLabel("Status: RUNNING")
        self.layout.addWidget(self.status_label)

        # Buttons 
        self.button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        self.save_button = QPushButton("Save CSV")
        self.save_button.setStyleSheet(
            "background-color: #2980b9; color: white; font-weight: bold; padding: 8px;"
        )

        # styling
        self.start_button.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; padding: 8px;"
        )
        self.stop_button.setStyleSheet(
            "background-color: #c0392b; color: white; font-weight: bold; padding: 8px;"
        ) 

        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.stop_button)
        self.button_layout.addWidget(self.save_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        # Data Storage 
        self.accel_data = [[], [], []]
        self.gyro_data = [[], [], []]

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)

        # Connect buttons
        self.start_button.clicked.connect(self.start_stream)
        self.stop_button.clicked.connect(self.stop_stream)
        self.save_button.clicked.connect(self.save_to_csv)

        # Start initially
        self.timer.start(100)

    #  Start 
    def start_stream(self):
        self.timer.start(100)
        self.status_label.setText("Status: RUNNING")

    # Stop 
    def stop_stream(self):
        self.timer.stop()
        self.status_label.setText("Status: STOPPED")

    # Update
    def update_data(self):
        accel, gyro, orient = get_imu_data()

        for i in range(3):
            self.accel_data[i].append(accel[i])
            self.gyro_data[i].append(gyro[i])

            self.accel_data[i] = self.accel_data[i][-100:]
            self.gyro_data[i] = self.gyro_data[i][-100:]

        # Update graphs
        self.accel_x.setData(self.accel_data[0])
        self.accel_y.setData(self.accel_data[1])
        self.accel_z.setData(self.accel_data[2])

        self.gyro_x.setData(self.gyro_data[0])
        self.gyro_y.setData(self.gyro_data[1])
        self.gyro_z.setData(self.gyro_data[2])

        # Update orientation
        self.roll_label.setText(f"Roll: {orient[0]:.2f}°")
        self.pitch_label.setText(f"Pitch: {orient[1]:.2f}°")
        self.yaw_label.setText(f"Yaw: {orient[2]:.2f}°")

        self.log_data.append([
        self.time_step,
        accel[0], accel[1], accel[2],
        gyro[0], gyro[1], gyro[2],
        orient[0], orient[1], orient[2]
        ])

        self.time_step += 1

    def save_to_csv(self):
        with open("imu_data.csv", "w", newline="") as file:
            writer = csv.writer(file)

            # Header
            writer.writerow([
                "Time",
                "Accel_X", "Accel_Y", "Accel_Z",
                "Gyro_X", "Gyro_Y", "Gyro_Z",
                "Roll", "Pitch", "Yaw"
            ])

            # Data
            writer.writerows(self.log_data)

        self.status_label.setText("Status: CSV Saved")
        