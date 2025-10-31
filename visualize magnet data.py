import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path = r"C:\Users\niant\Documents\Qist\MDP\Magnet-Positioner-Project\magnet_data\{number}.csv"
average = []
for i in range(50):
    print(i)
    if i > 17: #indexing misaligned from 18 onwards
        i += 1
    df = pd.read_csv(path.format(number=i), sep = ';', skiprows=7)
    df1 = df['By[mT]']
    average.append(abs(df1.mean())) #save the absolute magnetic field value
print(average)
distance = np.arange(50)
plt.plot(distance, average) #plot the stuff
plt.xlabel('Distance from chip center [cm]')
plt.ylabel('Mean field [mT]')
plt.show()
