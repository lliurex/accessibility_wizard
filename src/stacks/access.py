#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QListWidget,QSizePolicy
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSignalMapper,QEvent
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import subprocess
import dbus,dbus.service,dbus.exceptions
from . import functionHelper
QString=type("")

i18n={
	"COLOURS":_("Colours"),
	"FONTS":_("Fonts"),
	"CURSOR":_("Cursor"),
	"AIDS":_("Visual Aids"),
	"SCREEN":_("Screen Options"),
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("Accessibility options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Accessibility configuration"),
	"MENUDESCRIPTION":_("Set accesibility options"),
	"TOOLTIP":_("From here you can activate/deactivate accessibility aids"),
	"HIGHCONTRAST":_("Enable high contrast palette"),
	"INVERTENABLED":_("Invert screen colours"),
	"INVERTWINDOW":_("Invert windows colours"),
	"ANIMATEONCLICK":_("Show animation on click"),
	"SNAPHELPERENABLED":_("Show a grid when moving windows"),
	"LOOKINGGLASSENABLED":_("Activate eyefish effect"),
	"MAGNIFIERENABLED":_("Glass effect"),
	"ZOOMENABLED":_("Zoom effect"),
	"SYSTEMBELL":_("Acoustic system bell"),
	"FOCUSPOLICY":_("Set the policy focus"),
	"VISIBLEBELL":_("Visible bell"),
	"TRACKMOUSEENABLED":_("Track pointer"),
	"MOUSECLICKENABLED":_("Track click")
	}

class access(confStack):
	keybind_signal=Signal("PyObject")
	def __init_stack__(self):
		self.dbg=True
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-accessibility')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=1
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.config={}
		self.sysConfig={}
		self.wrkFiles=["kaccesrc","kwinrc"]
		self.blockSettings={"kwinrc":["FocusPolicy","lookingglassEnabled"]}
		self.wantSettings={}
		self.widgets={}
		self.widgetsText={}
		self.optionChanged=[]
		self.keymap={}
		for key,value in vars(Qt).items():
			if isinstance(value, Qt.Key):
				self.keymap[value]=key.partition('_')[2]
		self.modmap={
					Qt.ControlModifier: self.keymap[Qt.Key_Control],
					Qt.AltModifier: self.keymap[Qt.Key_Alt],
					Qt.ShiftModifier: self.keymap[Qt.Key_Shift],
					Qt.MetaModifier: self.keymap[Qt.Key_Meta],
					Qt.GroupSwitchModifier: self.keymap[Qt.Key_AltGr],
					Qt.KeypadModifier: self.keymap[Qt.Key_NumLock]
					}
	#def __init__

	def _load_screen(self):
		self.installEventFilter(self)
		self.box=QGridLayout()
		self.setLayout(self.box)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._grab_alt_keys)
		self.refresh=True
		row,col=(0,0)
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
			for kfile,sections in systemConfig.items():
				want=self.wantSettings.get(kfile,[])
				block=self.blockSettings.get(kfile,[])
				for section,settings in sections.items():
					for setting in settings:
						(name,data)=setting
						if name in block or (len(want)>0 and name not in want):
							continue
						desc=i18n.get(name.upper(),name)
						lbl=QLabel(desc)
						if (data.lower() in ("true","false")) or (data==''):
							btn=QCheckBox(desc)
							#btn=QPushButton(desc)
							#btn.setAutoDefault(False)
							#btn.setDefault(False)
							#btn.setCheckable(True)
							#btn.setStyleSheet(functionHelper.cssStyle())
							state=False
							if data.lower()=="true":
								state=True
							btn.setChecked(state)
							self.widgets.update({name:btn})
							self.box.addWidget(btn,row,col)
							col+=1
							btnName=functionHelper.getHotkey(name)
							if btnName:
								btn=QPushButton(btnName)
								sigmap_run.setMapping(btn,btnName)
								self.widgets.update({btnName:btn})
								self.widgetsText.update({btn:btnName})
								btn.clicked.connect(sigmap_run.map)
								self.box.addWidget(btn,row,col,Qt.Alignment(1))
							col+=1
							if col==2:
								row+=1
								col=0

						#ibtn.clicked
		#lst_settings.resizeRowsToContents()
		self.updateScreen()
	#def _load_screen

	def _grab_alt_keys(self,*args):
		desc=''
		btn=''
		self.btn=btn
		if len(args)>0:
			desc=args[0]
		if desc:
			btn=self.widgets.get(desc,'')
		if btn:
			btn.setText("")
			self.grabKeyboard()
			self.keybind_signal.connect(self._set_config_key)
			self.btn=btn
	#def _grab_alt_keys

	def _set_config_key(self,keypress):
		keypress=keypress.replace("Control","Ctrl")
		self.btn.setText(keypress)
		desc=self.widgetsText.get(self.btn)
		sysConfig=self.sysConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in sysConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					if setting==desc:
						valueArray=value.split(",")
						valueArray[0]=keypress
						valueArray[1]=keypress
						value=",".join(valueArray)
					dataTmp.append((setting,value))
				self.sysConfig[kfile][section]=dataTmp
		#if keypress!=self.keytext:
		#	self.changes=True
		#	self.setChanged(self.btn_conf)
	#def _set_config_key
	def eventFilter(self,source,event):
		sw_mod=False
		keypressed=[]
		if (event.type()==QEvent.KeyPress):
			for modifier,text in self.modmap.items():
				if event.modifiers() & modifier:
					sw_mod=True
					keypressed.append(text)
			key=self.keymap.get(event.key(),event.text())
			if key not in keypressed:
				if sw_mod==True:
					sw_mod=False
				keypressed.append(key)
			if sw_mod==False:
				self.keybind_signal.emit("+".join(keypressed))
		if (event.type()==QEvent.KeyRelease):
			self.releaseKeyboard()

		return False
	#def eventFilter

	def updateScreen(self):
		return
	#def _udpate_screen

	def _updateConfig(self,*args):
		return
	def writeConfig(self):
		sysConfig=self.sysConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in sysConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					btn=self.widgets.get(setting,'')
					if btn:
						value=btn.isChecked()
						if value:
							value="true"
						else:
							value="false"
					dataTmp.append((setting,value))
				self.sysConfig[kfile][section]=dataTmp

		functionHelper.setSystemConfig(self.sysConfig)
		self._reloadConfig()
		self.optionChanged=[]
		return