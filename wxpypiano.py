#! /usr/bin/python
# -*-  coding=utf8  -*-

#    Copyright (C) 2014 Guangmu Zhu <guangmuzhu@gmail.com>
#
#    This file is part of PyPiano.
#
#    PyPiano is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyPiano is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyChat.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import time
import thread
from pygame import mixer
import wx

reses = None
tone_dict = {
    "C": [40, 42, 44, 45 ,47, 49, 51],
    "F": [45 ,47, 49, 50, 52, 54, 56],
    "G": [47, 49, 51, 52, 54, 56, 58],
    "bB": [50, 52, 54, 55, 57 ,59, 61],
    "D": [42, 44, 46 ,47, 49, 51, 53],
    "bE": [43, 45, 47, 48, 50, 52, 54],
    "A": [49, 51, 53, 54, 56, 58 ,60],
    "bA": [48, 50, 52, 53, 55, 57 ,59],
    "E": [44, 46 ,48, 49, 51, 53, 55],
    "bD": [41, 43, 45 ,46, 48, 50, 52],
    "B": [51, 53, 55, 56, 58, 60, 62],
    "bG": [46, 48, 50, 51, 53, 55, 57],
    "#F": [46 ,48, 50, 51, 53, 55, 57],
    "bC": [39, 41, 43, 43 ,46, 48, 50],
    "#C": [41, 43, 45, 46 ,48, 50, 52],
    "bF": [44, 46 ,48, 49, 51, 53, 55],
    "#G": [48, 50, 52, 53, 55, 57 ,59]
    }
easy_map = []
tones = []
tones_index = 0
up_down = 0
record = []

global_flag = False
isplaying = False


def is_in_list(list, elem):
    for e in list:
        if e == elem:
            return True
    return False

def load_res(path):
    global reses
    
    reses = []
    for i in range(1, 89):
        reses.append(mixer.Sound(path + "/" + str(i) + ".wav"))

def create_easy_map(tone):
    global tone_dict, easy_map
    
    easy_map = [0] * 21
    i = 0
    for t in tone_dict[tone]:
        easy_map[i] = t - 12
        i = i + 1
    for t in tone_dict[tone]:
        easy_map[i] = t
        i = i + 1
    for t in tone_dict[tone]:
        easy_map[i] = t + 12
        i = i + 1
    
def down8():
    global easy_map, up_down
    
    for i in range(21):
        easy_map[i] = easy_map[i] - 12
    up_down = up_down - 1
        
def up8():
    global easy_map, up_down
    
    for i in range(21):
        easy_map[i] = easy_map[i] + 12
    up_down = up_down + 1
    
def reset_up_down():
    global tones, tones_index, up_down
    
    create_easy_map(tones[tones_index])
    up_down = 0
    
def prev_tone():
    global tones, tones_index, up_down
    
    if tones_index > 0:
        tones_index = tones_index - 1
        create_easy_map(tones[tones_index])
        up_down = 0
        return True
    else:
        return False

def next_tone():
    global tones, tones_index, up_down
    
    if tones_index < len(tones) - 1:
        tones_index = tones_index + 1
        create_easy_map(tones[tones_index])
        up_down = 0
        return True
    else:
        return False

def recordfcodes(codes):
    global record
    
    record = []
    flag = True
    codes = codes.split()
    for c in codes:
        if c == "T" or c == "Y" or c == " " or c == "G" or c == "H":
            record.append(c)
            continue
        if c.find("-") == -1:
            c = c.split("+")
            i = int(c[0])
            if i < 1 or i > 21:
                print >> sys.stderr, "error with num: %d" %i
                flag = False
            else:
                record.append((i, float(c[1])))
        else:
            temp = []
            c = c.split("+")
            codes = c[0].split("-")
            for sc in codes:
                i = int(sc)
                if i < 1 or i > 21:
                    print >> sys.stderr, "error with num: %d" %i
                    flag = False
                else:
                    temp.append(i)
            record.append((temp, float(c[1])))    
    return flag

def record2codes():
    global record
    
    codes = ""
    for r in record:
        if type(r) == str:
            codes = codes + r + " "
        elif type(r[0]) == int:
            codes = codes + str(r[0]) + "+" + str(r[1]) + " "
        else:
            codes = codes + "-".join([str(sr) for sr in r[0]]) + "+" + str(r[1]) + " "
    return codes[:-1]
    
class Frame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent = parent, id = id, title = "PyPiano", size = wx.Size(400,270), style =  wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.icon = wx.Icon("Piano.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour("wheat")
        
        self.title = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "PyPiano", pos = wx.Point(150, 0), size = wx.Size(50, 20), style = wx.ALIGN_CENTER)
        font = wx.Font(18, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.title.SetFont(font)
        self.title.SetForegroundColour("medium violet red")
        
        self.text1 = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "选择音调：", pos = wx.Point(20, 52), style = wx.ALIGN_LEFT)
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.text1.SetFont(font)
        
        self.toneBox = wx.ComboBox(parent = self.panel, id = wx.ID_ANY, pos = wx.Point(120, 50), size = wx.Size(60, 30), choices = ["C", "F", "G", "bB", "D", "bE", "A", "bA", "E",  "bD", "B", "bG", "#F", "bC", "#C", "bF", "#G"], style = wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.toneBox.SetValue("C")
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.toneBox.SetFont(font)
        self.toneBox.SetForegroundColour("coral")
        
        self.toneAddBt = wx.Button(parent = self.panel, id = wx.ID_ANY, label = "添加", pos = wx.Point(180, 50), size = wx.Size(60, 30))
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.toneAddBt.SetFont(font)
        self.toneAddBt.SetForegroundColour("sky blue")
        self.toneAddBt.Bind(wx.EVT_BUTTON, self.toneAddBtOnClick)
        
        self.toneDelBt = wx.Button(parent = self.panel, id = wx.ID_ANY, label = "删除", pos = wx.Point(250, 50), size = wx.Size(60, 30))
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.toneDelBt.SetFont(font)
        self.toneDelBt.SetForegroundColour("sky blue")
        self.toneDelBt.Bind(wx.EVT_BUTTON, self.toneDelBtOnClick)
        
        self.toneRetBt = wx.Button(parent = self.panel, id = wx.ID_ANY, label = "重置", pos = wx.Point(320, 50), size = wx.Size(60, 30))
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.toneRetBt.SetFont(font)
        self.toneRetBt.SetForegroundColour("sky blue")
        self.toneRetBt.Bind(wx.EVT_BUTTON, self.toneRetBtOnClick)
        
        self.text2 = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "已选择的音调：", pos = wx.Point(20, 100), style = wx.ALIGN_LEFT)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.text2.SetFont(font)
        
        self.toneAll = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "", pos = wx.Point(200, 100), style = wx.ALIGN_CENTER)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.toneAll.SetFont(font)
        self.toneAll.SetForegroundColour("coral")
        
        self.playBt = wx.Button(parent = self.panel, id = wx.ID_ANY, label = "演奏", pos = wx.Point(20, 150), size = wx.Size(80, 30))
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.playBt.SetFont(font)
        self.playBt.SetForegroundColour("sky blue")
        self.playBt.Bind(wx.EVT_BUTTON, self.playBtOnClick)
        
        self.replayBt = wx.Button(parent = self.panel, id = wx.ID_ANY, label = "回放", pos = wx.Point(115, 150), size = wx.Size(80, 30))
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.replayBt.SetFont(font)
        self.replayBt.SetForegroundColour("sky blue")
        self.replayBt.Bind(wx.EVT_BUTTON, self.replayBtOnClick)
        
        self.readBt = wx.Button(parent = self.panel, id = wx.ID_ANY, label = "读取", pos = wx.Point(210, 150), size = wx.Size(80, 30))
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.readBt.SetFont(font)
        self.readBt.SetForegroundColour("sky blue")
        self.readBt.Bind(wx.EVT_BUTTON, self.readBtOnClick)
        
        self.saveBt = wx.Button(parent = self.panel, id = wx.ID_ANY, label = "保存", pos = wx.Point(305, 150), size = wx.Size(80, 30))
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.saveBt.SetFont(font)
        self.saveBt.SetForegroundColour("sky blue")
        self.saveBt.Bind(wx.EVT_BUTTON, self.saveBtOnClick)
        
        self.text3 = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "当前音调：", pos = wx.Point(70, 200), style = wx.ALIGN_LEFT)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.text3.SetFont(font)
        
        self.toneNow = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "", pos = wx.Point(155, 200), style = wx.ALIGN_CENTER)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.toneNow.SetFont(font)
        self.toneNow.SetForegroundColour("coral")
        
        self.text4 = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "当前音高：", pos = wx.Point(240, 200), style = wx.ALIGN_LEFT)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.text4.SetFont(font)
        
        self.toneUpDown = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "", pos = wx.Point(320, 200), style = wx.ALIGN_CENTER)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.toneUpDown.SetFont(font)
        self.toneUpDown.SetForegroundColour("coral")
        
        self.copyright = wx.StaticText(parent = self.panel, id = wx.ID_ANY, label = "Made by Guangmu Zhu via Python", pos = wx.Point(200, 250), style = wx.ALIGN_RIGHT)
        font = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, faceName = "Microsoft YaHei UI")
        self.copyright.SetFont(font)
        self.copyright.SetForegroundColour("medium violet red")
        
    def updateInfo(self):
        global tones, tones_index, up_down
        
        self.toneNow.SetLabel(tones[tones_index])
        temp = "%+d" %(up_down * 8)
        self.toneUpDown.SetLabel(temp)
    
    def replay(self):
        global reses, easy_map, tones, tones_index, record
        global global_flag, isplaying
        
        if isplaying:
            return
        
        tones_index = 0
        create_easy_map(tones[tones_index])
        reset_up_down()
        
        for re in record:
            if not global_flag:
                break
            if type(re) != str:
                (r, t) = re
                if type(r) == int:
                    reses[easy_map[r - 1] - 1].set_volume(1.0)
                    reses[easy_map[r - 1] - 1].play()
                else:
                    for sr in r:
                        reses[easy_map[sr - 1] - 1].set_volume(1.0 / len(r))
                        reses[easy_map[sr - 1] - 1].play()
                time.sleep(t)
            else:
                if re == "T":
                    down8()
                if re == "Y":
                    up8()
                if re == " ":
                    reset_up_down()
                if re == "G":
                    prev_tone()
                if re == "H":
                    next_tone()
    
    def toneAddBtOnClick(self, event):
        global tones
        global isplaying
        
        if isplaying:
            return
        
        if tones == [] or not is_in_list(tones, self.toneBox.GetValue()):
            self.toneAll.SetLabel(self.toneAll.GetLabel() + self.toneBox.GetValue() + " ")
            tones = self.toneAll.GetLabel().strip().split()
            
    def toneDelBtOnClick(self, event):
        global tones
        global isplaying
        
        if isplaying:
            return
        
        if tones != [] and is_in_list(tones, self.toneBox.GetValue()):
            tones.remove(self.toneBox.GetValue())
            self.toneAll.SetLabel(" ".join(tones) + " ")
            
    def toneRetBtOnClick(self, event):
        global tones
        global isplaying
        
        if isplaying:
            return
        
        tones = []
        self.toneAll.SetLabel("")
            
    def playBtOnClick(self, event):
        global easy_map, tones, tones_index, up_down, record
        global isplaying
        
        if isplaying:
            return
        
        if tones == []:
            return
        tones_index = 0
        create_easy_map(tones[tones_index])
        reset_up_down()
        record = []
        
        self.playBt.SetLabel("演奏中")
        isplaying = True
        
        self.updateInfo()

        self.panel.Bind(wx.EVT_KEY_DOWN, self.playOnKeyDown)
        self.panel.Bind(wx.EVT_KILL_FOCUS, self.panelOnKillFocus)        
        self.panel.SetFocusIgnoringChildren()

    def panelOnKillFocus(self, event):
        self.panel.SetFocusIgnoringChildren()
        
    def playOnKeyDown(self, event):
        global reses, easy_map, tones, tones_index, up_down, record
        global isplaying

        if tones == []:
            return
        if event.GetKeyCode() < 0 or event.GetKeyCode() > 256:
            return
        c = chr(event.GetKeyCode()).lower()
        
        if c == '\r':
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            
            tones_index = 0
            create_easy_map(tones[tones_index])
            reset_up_down()
            
            self.playBt.SetLabel("演奏")
            isplaying = False
            
            self.updateInfo()
            
            self.panel.Bind(wx.EVT_KEY_DOWN, None)
            self.panel.Bind(wx.EVT_KILL_FOCUS, None)
        
        if c == "t":
            down8()
            self.updateInfo()
            record.append("T")
        
        if c == "y":
            up8()
            self.updateInfo()
            record.append("Y")
        
        if c == " ":
            reset_up_down()
            self.updateInfo()
            record.append(" ")
        
        if c == "g":
            if prev_tone():
                self.updateInfo()
                record.append("G")
        
        if c == "h":
            if next_tone():
                self.updateInfo()
                record.append("H")
            
        if c == "z":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((1, time.time()))
            reses[easy_map[0] - 1].play()
            
        if c == "x":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((2, time.time()))
            reses[easy_map[1] - 1].play()
            
        if c == "c":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((3, time.time()))
            reses[easy_map[2] - 1].play()
            
        if c == "v":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((4, time.time()))
            reses[easy_map[3] - 1].play()
            
        if c == "m":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((5, time.time()))
            reses[easy_map[4] - 1].play()
            
        if c == ",":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((6, time.time()))
            reses[easy_map[5] - 1].play()
            
        if c == ".":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((7, time.time()))
            reses[easy_map[6] - 1].play()
        
        if c == "a":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((8, time.time()))
            reses[easy_map[7] - 1].play()
            
        if c == "s":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((9, time.time()))
            reses[easy_map[8] - 1].play()
            
        if c == "d":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((10, time.time()))
            reses[easy_map[9] - 1].play()
            
        if c == "f":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((11, time.time()))
            reses[easy_map[10] - 1].play()
            
        if c == "j":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((12, time.time()))
            reses[easy_map[11] - 1].play()
            
        if c == "k":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((13, time.time()))
            reses[easy_map[12] - 1].play()
            
        if c == "l":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((14, time.time()))
            reses[easy_map[13] - 1].play()
        
        if c == "q":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((15, time.time()))
            reses[easy_map[14] - 1].play()
            
        if c == "w":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((16, time.time()))
            reses[easy_map[15] - 1].play()
            
        if c == "e":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((17, time.time()))
            reses[easy_map[16] - 1].play()
            
        if c == "r":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((18, time.time()))
            reses[easy_map[17] - 1].play()
            
        if c == "u":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((19, time.time()))
            reses[easy_map[18] - 1].play()
            
        if c == "i":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((20, time.time()))
            reses[easy_map[19] - 1].play()
            
        if c == "o":
            for i in range(-1, -len(record) - 1, -1):
                if type(record[i]) != str:
                    record[i] = (record[i][0], time.time() - record[i][1])
                    break
            record.append((21, time.time()))
            reses[easy_map[20] - 1].play()
    
    def replayBtOnClick(self, event):
        global tones, tones_index, record
        global global_flag, isplaying
        
        if isplaying:
            return

        if tones == [] or record == []:
            return
        
        global_flag = True
        self.dialog = wx.MessageDialog(self, "正在回放...", caption="PyPiano", style = wx.OK | wx.CANCEL | wx.STAY_ON_TOP)
        thread.start_new_thread(self.replay, ())
        self.dialog.ShowModal()
        global_flag = False
        self.dialog.Destroy()
        
        tones_index = 0
        reset_up_down()
        self.updateInfo()
        
    def readBtOnClick(self, event):
        global tones, tones_index, record
        global isplaying
        
        if isplaying:
            return

        self.dialog = wx.FileDialog(self, "选择文件", os.getcwd(), "", "PyPiano文件(*.ppo)|*.ppo|所有文件(*)|*", wx.OPEN)
        if self.dialog.ShowModal() == wx.ID_OK:
            in_f = open(self.dialog.GetPath(), "r")
            tone = in_f.readline().strip()
            tones = tone.split()
            tones_index = 0
            reset_up_down()
            create_easy_map(tones[tones_index])
            codes = in_f.readline().strip()
            in_f.close()
            self.dialog.Destroy()
            if not recordfcodes(codes):
                self.dialog = wx.MessageDialog(self, "文件格式错误！", caption="PyPiano", style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.STAY_ON_TOP)
                self.dialog.ShowModal()
                tones = []
                tones_index = 0
                record = []
            else:
                self.toneAll.SetLabel(" ".join(tones) + " ")
                self.updateInfo()
        
    def saveBtOnClick(self, event):
        global tones
        global isplaying
        
        if isplaying:
            return

        self.dialog = wx.FileDialog(self, "保存文件", os.getcwd(), "", "PyPiano文件(*.ppo)|*.ppo", wx.SAVE | wx.OVERWRITE_PROMPT)
        if self.dialog.ShowModal() == wx.ID_OK:
            path = self.dialog.GetPath()
            if path[-4:] != ".ppo":
                path = path + ".ppo"
            out_f = open(path, "w")
            out_f.truncate()
            out_f.write(" ".join(tones) + "\n")
            out_f.write(record2codes())
            out_f.flush()
            out_f.close()
            self.dialog.Destroy()
    
class App(wx.App):
    def OnInit(self):
        self.frame = Frame(parent = None, id = wx.ID_ANY)
        self.frame.Center()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        
        return True
    
    def OnExit(self):
        mixer.stop()
        mixer.quit()

def main(argv):
    mixer.init(44100)
    mixer.set_num_channels(20)
    load_res("./res")
    
    app = App()
    app.MainLoop()
    
if __name__ == "__main__":
    os.chdir("/home/guangmu/Apps/pypiano/")
    main(sys.argv[1:])
