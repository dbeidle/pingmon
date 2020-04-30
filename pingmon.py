import os
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header


# Hosts to check
hosts = ["192.168.1.1", "192.168.1.2", "192.168.1.254", "192.168.1.3"]
# File name of output to retain statuses
FILE_NAME = 'hosts_stats.json'
# E-mail address to send notification to
email_address = "receiver@example.com"
# Send from address
from_address = "server@example.com"
# Mail server password
password = "secret"

# Empty Results List
results_list = []

def mail(body_txt, subject_txt):
    server = smtplib.SMTP("smtp.gmail.com", 587)  # Gmail smtp server & port listed Modify for your own server
    server.ehlo()
    server.starttls()
    server.login(from_address, password)
    body = body_txt
    msg = MIMEText(body, 'plain', 'utf-8')
    subject = subject_txt
    msg["Subject"] = Header(subject, 'utf-8')
    from_ = from_address
    to = email_address
    msg["From"] = Header(from_, 'utf-8')
    msg["To"] = Header(to, 'utf-8')
    txt = msg.as_string()
    server.sendmail(from_, to, txt)

def ping(host):
    response = os.system('ping -c 1 {}'.format(host))
    date = datetime.datetime.now().isoformat()
    return  { "date": date, "host": host, "status": 'UP' if response == 0 else 'DOWN'}

def createFile():
    # [{"date": "2020-04-29T20:20:50.816327", "host": "192.168.1.1", "status": "DOWN"}]

    hostfile = []
    for host in hosts:
        hostfile.append({"host": host, "status": "unknown", "date": datetime.datetime.now().isoformat()})
    with open(FILE_NAME, "w") as fc:
        fc.write(json.dumps(hostfile))
        fc.close()



if __name__ == "__main__":

    # Open status file, Create list of previous statuses, close file and parse JSON to Python iterable.
    try:
        with open(FILE_NAME, 'r') as fr:
            previous_results = fr.read()
            fr.close()
            pr = json.loads(previous_results)
    except:
        createFile()
        with open(FILE_NAME, "r") as fr:
            new_results = fr.read()
            fr.close()
            pr = json.loads(new_results)

    # Ping each host and return all in list
    result = list(map(ping, hosts))
    exists = []
    for record in pr:
        exists.append(str(record["host"]))
    pass

    for entry in result:
        if entry["host"] in exists:
            for record in pr:
                if record["host"] == entry["host"]:
                    if entry["status"] != record["status"]:

                        # Convert Date/time entries to datetime.datetime format for subtraction:
                        d1 = datetime.datetime.strptime(record["date"], "%Y-%m-%d" + 'T' + "%H:%M:%S.%f")
                        d2 = datetime.datetime.strptime(entry["date"], "%Y-%m-%d" + 'T' + "%H:%M:%S.%f")

                        # Subtract oldest time from newest time to get length of time up/down respectively
                        d3 = d2 - d1

                        # Convert time to string
                        t = str(d3)
                        t = t.split(":")

                        # Break out hours/minutes/seconds
                        h = t[0]
                        m = t[1]

                        # Convert seconds into float then into int and back into string to get rid of decimal places
                        s = str(int(float(t[2])))

                        # Write mail body and subject
                        body1 = "Young Padwan, \r\n\r\n There is a disturbance in the force."
                        body2 = "\r\n\r\n Change in status to " + entry["host"] + " to " + entry["status"] + "."
                        body3 = "\r\n\r\n Was " + record["status"] + " for " + h + " hours " + m + " minutes " + s +\
                                " seconds."
                        body4 = "\r\n\r\n -Yoda"
                        body_txt = str(body1) + str(body2) + str(body3) + str(body4)
                        subject_txt = "Host %s is %s" % (entry["host"], entry["status"])

                        # Send mail
                        mail(body_txt, subject_txt)

                        # Add status changed entry to new list
                        results_list.append(entry)
                    else:
                        # Add non-status changed entries to new list
                        results_list.append(record)
        else:
            results_list.append(entry)

    # Write results_list to file in JSON format
    results_written = False
    if not results_written:
        results_written = True
        with open(FILE_NAME, 'w') as f:
            f.write(json.dumps(results_list))
            f.close()


