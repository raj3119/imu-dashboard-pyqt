import numpy as np

def get_imu_data():
    accel = np.random.randn(3)
    gyro = np.random.randn(3)
    orient = np.random.uniform(-180, 180, 3)
    return accel, gyro, orient