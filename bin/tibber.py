#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import matplotlib.pyplot as plt
import requests
import time
import datetime
import locale
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag

# Plugin Config
lbpconfigdir = os.popen("perl -e 'use LoxBerry::System; print $lbpconfigdir; exit;'").read()
lbpdatadir = os.popen("perl -e 'use LoxBerry::System; print $lbpdatadir; exit;'").read()
lbplogdir = os.popen("perl -e 'use LoxBerry::System; print $lbplogdir; exit;'").read()
try:
    with open(lbpconfigdir + '/plugin.json') as f:
        global pconfig
        pconfig = json.load(f)
except:
    print("Cannot read plugin configuration")
    sys.exit()

# MQTT Config
mqttconfig = dict()
mqttconfig['server'] = os.popen("perl -e 'use LoxBerry::IO; my $mqttcred = LoxBerry::IO::mqtt_connectiondetails(); print $mqttcred->{brokerhost}; exit'").read()
mqttconfig['port'] = os.popen("perl -e 'use LoxBerry::IO; my $mqttcred = LoxBerry::IO::mqtt_connectiondetails(); print $mqttcred->{brokerport}; exit'").read()
mqttconfig['username'] = os.popen("perl -e 'use LoxBerry::IO; my $mqttcred = LoxBerry::IO::mqtt_connectiondetails(); print $mqttcred->{brokeruser}; exit'").read()
mqttconfig['password'] = os.popen("perl -e 'use LoxBerry::IO; my $mqttcred = LoxBerry::IO::mqtt_connectiondetails(); print $mqttcred->{brokerpass}; exit'").read()

# Setup Local
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

# Arguments
parser = argparse.ArgumentParser(description='Tibber Graph 4 today / tomorrow')
parser.add_argument('-d','--do', help='-d today / -d tomorrow', required=True)
args = vars(parser.parse_args())
time_windows = 'today'
if args['do'] == 'today':
    time_windows = 'today'
elif args['do'] == 'tomorrow':
    time_windows = 'tomorrow'

pic = (pconfig["path"] + '/tibber_graph_' +  args['do'] + '.png')

# Set Request Data
print ("Getting data from Tibber API...")
url = "https://api.tibber.com/v1-beta/gql"
headers = {
        "Authorization": 'Bearer ' + pconfig["api_key"],
        "Content-Type": "application/json",
    }
query = """
{
  viewer {
    homes {
      currentSubscription{
        priceInfo{
          current{
            total
            energy
            tax
            startsAt
          }
          today {
            total
            energy
            tax
            startsAt
          }
          tomorrow {
            total
            energy
            tax
            startsAt
          }
        }
      }
    }
  }
}
"""

# Request Data from Tibber
data = {"query": query}
response = requests.post(url, json=data, headers=headers)
response_data = response.json()
if not "data" in response_data:
    print("Could not get data from Tibber API. Correct API Key used?")
    sys.exit()

# Setup Datapoints
homes = response_data['data']['viewer']['homes']
subscriptions = []
for home in homes:
    subscription = home.get('currentSubscription')
    if subscription:
        subscriptions.append(subscription)
price_infos = []
for subscription in subscriptions:
    price_info = subscription.get('priceInfo')
    if price_info:
        price_infos.append(price_info)
if time_windows =='tomorrow':
    today_data = price_infos[0]["tomorrow"]
else:
    today_data = price_infos[0]["today"]
x = [interval["startsAt"] for interval in today_data ]
y = [interval["total"] for interval in today_data]
highest_index = y.index(max(y))
highest_x = x[highest_index]
highest_y = y[highest_index]
highest_y = round(highest_y, 3)
lowest_index = y.index(min(y))
lowest_x = x[lowest_index]
lowest_y = y[lowest_index]
lowest_y = round(lowest_y, 3)
highest_y = max(y)
lowest_y = min(y)
average_price = np.mean(y)
act_price = price_infos[0]["current"]["total"]

# Setup Date Datapoints
date = datetime.datetime.fromisoformat("2023-01-04T23:00:00.000+01:00")
dates = [datetime.datetime.fromisoformat(date_string) for date_string in x]
shortened_dates_0 = [date.strftime("%H") for date in dates]
shortened_dates_1 = [date.strftime("%-H") for date in dates]

# Setup Plot
figure = plt.style.use('dark_background')
figure = plt.figure(layout='tight')
plot = figure.add_subplot(111)
if time_windows == 'tomorrow':
    current_dates = datetime.datetime.today() + datetime.timedelta(days=1)
else:
    current_dates = datetime.datetime.now()
current_date=(current_dates .strftime("%a - %d. %b %Y"))
hour_now = current_dates.strftime('%-H')
colors = []
for i in shortened_dates_1:
  if i == hour_now:
    if time_windows == 'tomorrow':
        colors.append(pconfig['bar_color'])
    else:
        colors.append(pconfig['bar_active_color'])
  else:
    colors.append(pconfig['bar_color'])

# Plot Graph
print ("Creating Plot images...")
bar_container = plot.bar(shortened_dates_0, y, color=colors )
# Plot Lables
plot.bar_label(bar_container, fmt='{:,.4f} €', label_type='center', fontsize=14, color=pconfig['text_color'], rotation=90)
xlabels = plot.get_xaxis().get_ticklabels()
for label in xlabels:
    label.set_rotation(90)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# Plot Text
plt.text(-1.5, highest_y, '{}'.format('Tibber\n'), fontsize=20, fontweight='bold', ha='left', color=pconfig['text_color'])
if time_windows == 'today':
    plt.text(24.5, highest_y, 'akt. Preis: {:.4f} €\nØ Preis: {:.4f} €\n'.format(act_price, average_price), fontsize=14, ha='right', fontweight='bold', color=pconfig['text_color'])
else:
    plt.text(24.5, highest_y, '\nØ Preis: {:.4f} €\n'.format( average_price), fontsize=14, ha='right', fontweight='bold', color=pconfig['text_color'])
if time_windows == 'today':
    plt.text(6, highest_y, 'für heute:\n{}\n'.format(current_date), fontsize=14, ha='left', fontweight='bold', color=pconfig['text_color'])
else:
    plt.text(6, highest_y, 'für morgen:\n{}\n'.format(current_date), fontsize=14, ha='left', fontweight='bold', color=pconfig['text_color'])
# Setup Size/DPI
figure.set_size_inches(int(pconfig["plot_width"])/100, int(pconfig["plot_height"])/100)
figure.set_dpi(100)
# Save Picuture
picname = (pic)
figure.savefig(picname, transparent=True)

# Save Data to Json
print ("Saving JSON data...")
json_object_nice = json.dumps(response_data, indent=4)
json_object = json.dumps(response_data)
with open(pconfig['path'] + "/tibber_data.json", "w") as outfile:
    outfile.write(json_object_nice)

# Conncect to broker and publish data
if mqttconfig['server'] == "" or mqttconfig['port'] == "":
    print("Cannot find mqtt configuration. Do not publish data to MQTT broker.")
    sys.exit()

print ("Publishing data to MQTT broker...")
client = mqtt.Client()
client.connected_flag=False
client.on_connect = on_connect
if mqttconfig['username'] and mqttconfig['password']:
    client.username_pw_set(username = mqttconfig['username'],password = mqttconfig['password'])
client.connect(mqttconfig['server'], port = int(mqttconfig['port']))
client.publish(pconfig["topic"] + "/tibber", json_object, retain=1)
