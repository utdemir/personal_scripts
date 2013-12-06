#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import sys
import time
import notify2
import os.path

FULL_PERCENT = 96
CRITICAL_PERCENT = 3
NOTIFY = (15, 30)

BATTERY_PATH = "/sys/class/power_supply/BAT0"
AC_PATH = "/sys/class/power_supply/ADP1"

notify2.init("battery notifier")

max_voltage = int(open(os.path.join(BATTERY_PATH, "energy_full")).read())

def notify(summary, urgency):
    n = notify2.Notification(summary)
    n.set_urgency(urgency)
    n.show()

def get_current_voltage():
    current_voltage = int(open(os.path.join(BATTERY_PATH, "energy_now")).read())
    current = 100 / max_voltage * current_voltage
    return current

is_charging = None
current = 0

while True:
    time.sleep(1)
    
    old_is_charging = is_charging
    is_charging = open(os.path.join(AC_PATH, "online")).read().strip() == "1" 

    if is_charging != old_is_charging:
        if is_charging:
            status = "charging"
        else:
            status = "discharging"
        notify("Battery is {}".format(status), notify2.URGENCY_LOW)


    before, current = current, get_current_voltage()
    
    if before == current: continue

    is_full = current >= FULL_PERCENT

    if before < FULL_PERCENT <= current: 
        notify("Battery is full", notify2.URGENCY_LOW)

    if current <= CRITICAL_PERCENT < before:
        notify("Battery is critical", notify2.URGENCY_CRITICAL)

    for n in NOTIFY:
        if current <= n < before:
            notify("Battery is %{}".format(n), notify2.URGENCY_NORMAL)


