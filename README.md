# *Screenshots:*
Report HTML:
![image](https://github.com/user-attachments/assets/9ca1bdff-04c1-4d1e-8a99-7424cdbad0d8)
Data Storing:
![image](https://github.com/user-attachments/assets/d089a664-53b7-4147-95e0-6bf8d9270665)
Email Alert:
![image](https://github.com/user-attachments/assets/e47bf568-3b78-4bd5-86d3-c75852c193e3)






### -Detailed Description:
This script is designed to be a robust network monitoring and alerting tool. Here's a breakdown of its functionality:
### -Device Discovery:
It starts by discovering all the devices connected to your specified network *(network variable)*. It does this using **ARP** *(Address Resolution Protocol)* requests to identify the IP and MAC addresses of each device.
## Ping Monitoring:
The script continuously pings each discovered device to check its responsiveness. This involves sending ICMP echo requests (ping packets) and measuring the round-trip time (RTT).
### Status Tracking:
The script keeps track of whether each device is "up" (reachable) or "down" (unreachable). If a device's status changes, it logs the event.
### Performance Logging:
For each device, it records the best (lowest) and worst (highest) ping times observed, along with the corresponding timestamps. This data is stored in a MySQL database for later analysis.
### Email Alerts:
If a device goes down or experiences unusually high latency (a customizable threshold), the script sends an email alert to the specified address. This allows you to quickly respond to potential network issues.
### Dynamic HTML Report:
The script dynamically generates an HTML report (network.html) that displays the status of each device, including its current ping time, best ping time, and worst ping time. The report is updated in real-time so you can monitor the network from a web browser.
# Why Environment Variables?
Storing sensitive information like your MySQL and email credentials directly in the code is a security risk. By using environment variables, you keep this information separate and secure. Here's how to set them:
## Windows:
Open a command prompt.<br>
Use commands like set SENDER_EMAIL=your_email@gmail.com to set each variable
## macOS/Linux:
Open a terminal.
Use commands like export SENDER_EMAIL=your_email@gmail.com to set each variable.
# Tutorial
## 1.Prerequisites:
Ensure you have Python 3.x installed.
Install required libraries: pip install scapy mysql-connector-python
Have a MySQL server running and create a database named netstat with the provided table structure.
Set up your environment variables (see above).
## 2.Configuration:
Replace the network variable with your network's IP address range (e.g., "192.168.1.0/24").
Adjust the pause variable to control the scanning frequency.
Customize email alert thresholds (if needed).
## 3.Run:
Save the code as a Python file (e.g., network_monitor.py).
Open a terminal or command prompt.
Navigate to the directory where you saved the file.
Execute: python network_monitor.py
## 4.View Report:
Open network.html in your web browser to see the real-time network status.










