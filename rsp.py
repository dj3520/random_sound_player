import sys, time, random
from glob import iglob
from math import floor

import logging
log = logging.getLogger()
format = logging.Formatter(fmt="%(asctime)s [%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%m/%d/%Y %H:%M:%S")

import logging.handlers
handler = logging.handlers.RotatingFileHandler("RSP.log", backupCount=4, encoding="utf-8", mode="w")
handler.setFormatter(format)
log.addHandler(handler)

con = logging.StreamHandler(sys.stdout)
con.setFormatter(format)
log.addHandler(con)

log.setLevel(10)

from deps import player
import tkinter as tk
import tkinter.ttk as ttk
import audioop
import threading

rootwin = tk.Tk()
rootwin.title("Random Sound Player ~ by DJ3520")

start_delay = tk.DoubleVar(name="Start Delay")
high_delay = tk.DoubleVar(name="High Delay")
low_delay = tk.DoubleVar(name="Low Delay")
decrement_delay = tk.DoubleVar(name="Decrement Delay")

area = tk.Frame(rootwin)
area.grid(row=0, column=2)
center = tk.Frame(rootwin)
center.grid(row=0, column=1)
volume = tk.DoubleVar(name="Volume")
chk = tk.Scale(rootwin, variable=volume, from_=1, to=0, length=300, resolution=0.01, orient=tk.VERTICAL, width=10, sliderrelief=tk.FLAT, takefocus=True)
chk.grid(row=0, column=0)

chk = tk.Label(area, text="First delay.", justify=tk.LEFT)
chk.grid(row=0, column=0)
chk = tk.Spinbox(area, textvariable=start_delay, width=4, from_=1, to=60)
chk.grid(row=0, column=1)
chk = tk.Label(area, text="Highest delay.", justify=tk.LEFT)
chk.grid(row=1, column=0)
chk = tk.Spinbox(area, textvariable=high_delay, width=4, from_=1, to=60)
chk.grid(row=1, column=1)
chk = tk.Label(area, text="Decrease delay.", justify=tk.LEFT)
chk.grid(row=2, column=0)
chk = tk.Spinbox(area, textvariable=decrement_delay, width=4, from_=0, to=60, increment=0.1)
chk.grid(row=2, column=1)
chk = tk.Label(area, text="Lowest delay.", justify=tk.LEFT)
chk.grid(row=3, column=0)
chk = tk.Spinbox(area, textvariable=low_delay, width=4, from_=0.5, to=60, increment=0.5)
chk.grid(row=3, column=1)

status = tk.Label(center, text="\nReady\n", justify=tk.LEFT, width=20, background="#00FF00")
status.grid()
playb = tk.Button(area, text="Start")
playb.grid(row=6, column=0)

start_delay.set(10)
high_delay.set(5)
decrement_delay.set(0.1)
low_delay.set(1)
volume.set(1)

countdown = 0
def count_it_down(number):
  global countdown
  countdown = floor(number * 60)
  while countdown > 0:
    if countdown < 6: color = "#FF0000"
    elif countdown < 31: color = "#FFFF00"
    else: color = "#00FF00"
    # remain = datetime.datetime.now() + datetime.timedelta(seconds=remain)
    remain = time.strftime('%M:%S', time.gmtime(countdown))
    status.config(text="\n"+remain+"\n", background=color)
    countdown -= 1
    time.sleep(1)

snds = []
def build_list():
  global snds
  snds = []
  log.info("Rebuild sound library")
  for i in iglob("snds\\*"):
    snds.append(i)
    log.debug(i)

state = "Ready"
def do_the_stuff():
  global state
  try:
    build_list()
    p = player.player()
    # Generates console window. Annoying but prevents window focus stealing for the time being.
    p.commit(b'')
    count_it_down(start_delay.get())
    current_delay = high_delay.get()

    while state == "Running":
      if len(snds) < 1: build_list()
      else:
        i = random.choice(snds)
        snds.remove(i)
        log.info("Chose to play {}".format(i))
        c = player.input(i)
        while True:
          d = c.read(192000) #about 1 second
          if d is None: break
          d = audioop.mul(d, 2, volume.get())
          p.commit(d)
        del c
        count_it_down(current_delay)
        current_delay -= decrement_delay.get()
        if current_delay < low_delay.get(): current_delay = low_delay.get()
        log.info("New delay: {}".format(current_delay))

    playb.configure(text="Start")
    status.config(text="\nReady\n", background="#00FF00")
  except Exception as e:
    log.critical("Exception in player thread! ", exc_info=e)
    return

def button_push():
  global state, countdown
  if state == "Ready":
    playthread = threading.Thread(target=do_the_stuff, name="Sound Thread", daemon=True)
    rootwin.after_idle(playthread.start)
    playb.configure(text="Stop")
    state = "Running"
  else:
    countdown = 0
    state = "Ready"

  log.info("Button press. State: {}".format(state))

playb.config(command=button_push)

rootwin.mainloop()