from pandas import read_csv
import matplotlib.pyplot as plt


# Read measurements from CSV file
df = read_csv(r'./magnet_data/magnet_x-axis_measurement_data.csv')

# Select columns
df = df[['Magnet-sensor distance [cm]', r'By[mT]']]
# Group by distance
df = df.groupby(['Magnet-sensor distance [cm]'])
# Compute absolute value of mean B field at each distance
means = df.mean().abs()

# Plot
plt.title('Magnet field measurements with Hall sensor')
plt.plot(means)
plt.xlabel('Magnet-sensor distance [cm]')
plt.ylabel('Mean magnetic field [mT]')
plt.show()
