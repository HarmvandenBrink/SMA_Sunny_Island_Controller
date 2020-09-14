# SMA Sunny Island Controller
A controller to read out and send commands to a SMA Sunny Island battery inverter

This code was used in a home built Home Energy Management System (HEMS), to include a battery into a smart home. You can read more about it in my blog post: [How I built a HEMS with solar, a battery and a charge station (in Python)](https://medium.com/@harmvandenbrink/how-i-built-a-hems-with-solar-a-battery-and-a-charge-station-in-python-d5b51e60fd1c?source=friends_link&sk=f5e9302a02ea29065c3f677ecf1b8ed8)

# How to use the code
## Read out values

```python
print readSMAValues() # To print all values
print readSMAValues('ChaState') # To read a single value, in this case the State of Charge (SoC)
```

## Control the battery

```python
changePowerOfTheInverter(1000) # To discharge the battery with 1000 Watt (1 kW)
changePowerOfTheInverter(-2000) # To charge the battery with 2000 Watt (2 kW)
```

# Disclaimer

The code within this repository comes with no guarantee, the use of this code is your responsibility.

I take NO responsibility and/or liability for how you choose to use any of the source code available here. By using any of the files available in this repository, you understand that you are AGREEING TO USE AT YOUR OWN RISK.
