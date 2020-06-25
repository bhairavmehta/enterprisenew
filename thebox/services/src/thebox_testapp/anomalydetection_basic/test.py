import numpy as np
import matplotlib.pyplot as plt

def displayData(input):
    plt.clf()
    # Create data points and offsets
    x = np.linspace(0.0,64, 64)
    y = input[0,:,:]
    # Set the plot curve with markers and a title
    for i in range(y.shape[1]):
        plt.plot(x,y[:,i])

    plt.xlim(left = 0, right = 65)
    plt.ylim(bottom = 0, top = 20)
    plt.xlabel("Time")
    plt.ylabel("Sensor Reading")
    plt.title("Readings From Sensor")
    plt.show(block=False)
    plt.pause(100)



data = np.zeros([1,64,10])

data_delta = {
    "pi3" : 1,
    "sesor1" : 0,
    "sesor2" : 0,
    "sesor3" : 0,
    "sesor4" : 0,
    "sesor5" : 0,
    "sesor6" : 0,
    "sesor7" : 0,
    "sesor8" : 0,
    "sesor9" : 1
}
data_delta_array = np.array([val for val in data_delta.values()])

print(data_delta_array)
print("shape of delta_array" + str(data_delta_array.shape))
print("shape of data" + str(data.shape))



data = np.append([[data_delta_array]],data[:,:63,:] ,axis=1)
print("merged shape of data" + str(data.shape))
print(data)
data = np.append([[data_delta_array]],data[:,:63,:] ,axis=1)
print("merged shape of data" + str(data.shape))
print(data)
displayData(data)

