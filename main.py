import os
import subprocess
from time import sleep
from datetime import datetime
from scapy.all import ARP, Ether, srp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector

# Database Connection (using environment variables)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database='netstat',
    auth_plugin='mysql_native_password'
)

# Email Configuration (using environment variables)
sender_email = os.environ.get("SENDER_EMAIL")
receiver_email = os.environ.get("RECEIVER_EMAIL")
password = os.environ.get("EMAIL_PASSWORD")
mycursor = mydb.cursor()

def discover_devices(network):
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=3, verbose=0)[0]
    devices = [{'ip': received.psrc, 'mac': received.hwsrc} for sent, received in result]
    return devices

def extract_ping_time(ping_output):
    try:
        time_value = ping_output.split("time=")[1].split(" ")[0].strip().replace('ms', '')
        return f"{float(time_value)} ms"
    except Exception as e:
        print(f"Failed to extract time from ping output: {str(e)}")
        return None

def ping(host):
    try:
        result = subprocess.run(['ping', '-c', '1', host], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return 'success', result.stdout
        else:
            return 'failed', result.stderr
    except subprocess.TimeoutExpired:
        return 'failed', f'Timeout expired while pinging {host}'
    except Exception as e:
        return 'failed', str(e)

def send_email_alert(host, message):
    try:
        sender_email = "anoirusa69@gmail.com"
        receiver_email = "youanoir@gmail.com"
        password = "izjsiunzbirxvgxn"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"Alert: Issue with {host}"
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email alert sent for {host}: {message}")
    except Exception as e:
        print(f"Failed to send email alert: {str(e)}")

def log_device_status(device, ping_time):
    cursor = mydb.cursor()

    cursor.execute('SELECT best_ping, worst_ping FROM devices WHERE ip=%s', (device['ip'],))
    row = cursor.fetchone()

    if row is None:
        cursor.execute('''
            INSERT INTO devices (ip, mac, best_ping, worst_ping, best_ping_time, worst_ping_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (device['ip'], device['mac'], ping_time, ping_time, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    else:
        best_ping, worst_ping = row
        if ping_time is not None:
            ping_time_value = float(ping_time.split(" ")[0])
            best_ping_value = float(best_ping.split(" ")[0]) if best_ping else None
            worst_ping_value = float(worst_ping.split(" ")[0]) if worst_ping else None

            if best_ping_value is None or ping_time_value < best_ping_value:
                cursor.execute('''
                    UPDATE devices
                    SET best_ping = %s, best_ping_time = %s
                    WHERE ip = %s
                ''', (ping_time, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), device['ip']))

            if worst_ping_value is None or ping_time_value > worst_ping_value:
                cursor.execute('''
                    UPDATE devices
                    SET worst_ping = %s, worst_ping_time = %s
                    WHERE ip = %s
                ''', (ping_time, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), device['ip']))

    mydb.commit()
    cursor.close()

pause = 10
header = (
    "<meta http-equiv='refresh' content='4'>\n"
    "<title>Up/ Down App</title>\n"
    "<link rel='stylesheet' type='text/css' href='style.css'>\n"
    "<h1>Network Monitoring</h1>"
    "<table><tr><td class='titles' class='A'>IP+STATUS</td><td class='titles' class='B'>ACTUAL PING</td><td class='titles' class='C'>BEST PING</td><td class='titles' class='D'>WORST PING</td></tr></table>"
)

network = "192.168.1.0/24"
known_devices = {}

while True:
    body = "<table>"
    devices = discover_devices(network)
    current_ips = [device['ip'] for device in devices]

    for device in devices:
        if device['ip'] not in known_devices:
            known_devices[device['ip']] = {'mac': device['mac'], 'status': 'unknown'}

    for ip, info in known_devices.items():
        body += "\n\t<tr>\n"
        if ip in current_ips:
            response, output = ping(ip)
            if response == "success":
                print(f"{ip} is UP")
                info['status'] = 'up'
                body += f"\t\t<td class='A' style='background-color:lightgreen;box-shadow: 0 0 20px #00ff00;border-color:lightgreen;'>{ip} is UP</td>"
                time_value = extract_ping_time(output)
                if time_value is not None:
                    log_device_status({'ip': ip, 'mac': info['mac']}, time_value)
                    ping_time_value = float(time_value.split(" ")[0])
                    if ping_time_value <= 30:
                        body += f"\n\t\t<td class='B' style='background-color:lightgreen;box-shadow: 0 0 20px #00ff00;border-color:lightgreen;'>{time_value}</td>\n"
                    elif ping_time_value > 30 and ping_time_value <= 100:
                        body += f"\n\t\t<td class='B' style='background-color:#dede09;box-shadow: 0 0 20px yellow;border-color:#dede09;'>{time_value}</td>\n"
                    elif ping_time_value > 100 and ping_time_value <= 200:
                        body += f"\n\t\t<td class='B' style='background-color:orange;box-shadow: 0 0 20px orangered;border-color:orange;'>{time_value}</td>\n"
                    elif ping_time_value > 200 and ping_time_value <= 500:
                        body += f"\n\t\t<td class='B' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>{time_value}</td>\n"
                    else:
                        body += f"\n\t\t<td class='B' style='background-color:purple;box-shadow: 0 0 20px mediumpurple;border-color:purple;'>{time_value}</td>\n"
                        send_email_alert(ip, f"High latency detected: {time_value}")

                    cursor = mydb.cursor()
                    cursor.execute('SELECT best_ping, worst_ping FROM devices WHERE ip=%s', (ip,))
                    row = cursor.fetchone()
                    if row is not None:
                        best_ping, worst_ping = row
                        body += f"\n\t\t<td class='C'>{best_ping}</td>\n"
                        body += f"\n\t\t<td class='D'>{worst_ping}</td>\n"
                    cursor.close()
                else:
                    if "TTL=128" in output:
                        body += f"\n\t\t<td class='B' style='background-color:white;box-shadow: 0 0 20px white;border-color:white;'>0 ms</td>\n"
                        body += f"\n\t\t<td class='C'  style='background-color:white;box-shadow: 0 0 20px white;border-color:white;'>0 ms</td>\n"
                        body += f"\n\t\t<td class='D' style='background-color:white;box-shadow: 0 0 20px white;border-color:white;'>0 ms</td>\n"
                    else:
                        body += f"\n\t\t<td class='B' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"
                        body += f"\n\t\t<td class='C' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"
                        body += f"\n\t\t<td class='D' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"

            else:
                print(f"{ip} is DOWN or an issue occurred: {output.strip()}")
                info['status'] = 'down'
                log_device_status({'ip': ip, 'mac': info['mac']}, None)
                body += f"\t\t<td class='ISSUES' class='A' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>{ip} is DOWN or has an ISSUE</td>"
                body += f"\n\t\t<td class='B' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"
                body += f"\n\t\t<td  class='C' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"
                body += f"\n\t\t<td class='D' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"
                send_email_alert(ip, f"Host is DOWN or has an issue: {output.strip()}")
        else:
            if info['status'] == 'up':
                print(f"{ip} has gone DOWN")
                info['status'] = 'down'
                log_device_status({'ip': ip, 'mac': info['mac']}, None)
                send_email_alert(ip, f"Host {ip} has gone DOWN")
            body += f"\t\t<td class='ISSUES' class='A' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>{ip} is DOWN</td>"
            body += f"\n\t\t<td class='B' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"
            body += f"\n\t\t<td class='C' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"
            body += f"\n\t\t<td class='D' style='background-color:red;box-shadow: 0 0 20px #ff6900;border-color:red;'>-</td>\n"

        body += "\t</tr>"

    body += "\n</table>"
    html = f"{header}\n{body}"

    try:
        with open("network.html", "w") as file:
            file.write(html)
        print("HTML report updated successfully.")
    except Exception as e:
        print(f"Failed to update HTML report: {str(e)}")

    print("********")
    sleep(pause)
