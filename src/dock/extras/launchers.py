#!/usr/bin/python3
import os,sys,shutil
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QLineEdit,QHBoxLayout,QGridLayout,QComboBox,QFileDialog,QListWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSize
from QtExtraWidgets import QSearchBox,QStackedWindow,QStackedWindowItem,QHotkeyButton
from app2menu import App2Menu
from accesshelper import accesshelper
import gettext
_ = gettext.gettext

i18n={"ADD":_("Assign"),
	"CANCEL":_("Cancel"),
	"DESCRIPTION":_("Description"),
	"EFFECT":_("Toggle effect"),
	"EXECUTABLE":_("Application"),
	"EXECUTABLE_TOOLTIP":_("Press button to assign one action"),
	"EXEHOLDER":_("Executable path"),
	"EXETOOLTIP":_("Insert the executable path"),
	"HOTKEY":_("Shortcut"),
	"HOTKEY_PRESS":_("Press a key"),
	"ICON":_("Icon: "),
	"ICON_TOOLTIP":_("Push to change icon"),
	"NAME":_("Name: "),
	"NAME_PLACEHOLDER":_("Unassigned action"),
	"NAME_TOOLTIP":_("Insert desktop name"),
	"URLTOOLTIP":_("Insert the url for the site"),
	"URLHOLDER":_("https://example.com")
}

class actionSelector(QStackedWindowItem):
	def __init_stack__(self,mode=""):
		self.setProps(shortDesc=i18n.get("MENU"),
			longDesc=i18n.get("DESC"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.hideControlButtons()
		self.app2menu=App2Menu.app2menu()
		self.accesshelper=accesshelper.client()
		self.mode=mode
		self.fname=""
		self.btnCancel.clicked.connect(self._back)
	#def __init__

	def setMode(self,mode):
		self.mode=mode
	#def setMode

	def __initScreen__(self):
		layout=QGridLayout()
		self.setLayout(layout)
		inpSearch=QSearchBox()
		layout.addWidget(inpSearch,0,0,1,2)
		self.lstActions=QListWidget()
		layout.addWidget(self.lstActions,1,0,1,2)
		btnOk=QPushButton("Ok")
		btnOk.clicked.connect(self._addAction)
		layout.addWidget(btnOk,2,0,1,1)
		btnKo=QPushButton(i18n["CANCEL"])
		btnKo.clicked.connect(self._back)
		layout.addWidget(btnKo,2,1,1,1)
	#def __initScreen__

	def updateScreen(self):
		self.lstActions.clear()
		apps={}
		if self.mode=="apps":
			cats=self.app2menu.get_categories()
			for cat in cats:
				apps.update(self.app2menu.get_apps_from_category(cat.lower()))
			for name,data in apps.items():
				app=self.app2menu.get_desktop_info(data.get("path"))
				if app.get("NoDisplay","")==True:
					continue
				appicon=data.get("icon","")
				appname=data.get("name")
				appexe=data.get("exe")
				apppath=data.get("path")
				appdesc=app.get("Comment","")
				self.lstActions.addItem(appname)
				if os.path.exists(appicon):
					qicon=QtGui.QIcon(appicon)
				else:
					qicon=QtGui.QIcon.fromTheme(appicon)
				self.lstActions.item(self.lstActions.count()-1).setIcon(qicon)
				itemData={"type":"desktop","Exec":appexe,"Name":appname,"Icon":appicon,"Comment":appdesc,"Path":apppath}
				self.lstActions.item(self.lstActions.count()-1).setData(Qt.UserRole,itemData)
		else:
			plugins=self.accesshelper.getKWinEffects()
			plugins.update(self.accesshelper.getKWinScripts())
			for name,data in plugins.items():
				name=data.get("KPlugin",{}).get("Name","")
				if len(name)==0:
					continue
				self.lstActions.addItem(data.get("KPlugin",{}).get("Name"))
				plugType="script"
				if "Category" in data.get("KPlugin",{}):
					plugType="effect"
				icon=data.get("KPlugin",{}).get("Icon")
				plugid=data.get("KPlugin",{}).get("Id")
				appname=data.get("KPlugin",{}).get("Name")
				desc=data.get("KPlugin",{}).get("Comment")
				itemData={"type":plugType,"Exec":plugid,"Name":appname,"Icon":icon,"Comment":desc,"Path":""}
				self.lstActions.item(self.lstActions.count()-1).setData(Qt.UserRole,itemData)
	#def updateScreen

	def setParms(self,*args):
		self.mode="effects"
		if args[0]==i18n["EXECUTABLE"]:
			self.mode="apps"
		if len(args)>1:
			if os.path.exists(args[1]):
				self.fname=args[1]
	#def setParms

	def _addAction(self):
		self.parent.setCurrentStack(0,parms=self.lstActions.currentItem().data(Qt.UserRole))
	#def _addAction

	def _back(self,*args):
		self.parent.setCurrentStack(0)
	#def _back
#class actionSelector

class portrait(QStackedWindowItem):
	accepted=Signal("PyObject")
	def __init_stack__(self):
		self.setProps(shortDesc=i18n.get("MENU"),
			longDesc=i18n.get("DESC"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=2,
			visible=True)
		self.appIcon="shell"
		self.fName=""
		self.action={}
		self.hideControlButtons()
	#def __init_stack__

	def __initScreen__(self):
		box=QGridLayout()
		wdg=QWidget()
		hbox=QHBoxLayout()
		wdg.setLayout(hbox)
		self.cmbApp=QComboBox()
		self.cmbApp.addItem(i18n["EFFECT"])
		self.cmbApp.addItem(i18n["EXECUTABLE"])
		hbox.addWidget(self.cmbApp,Qt.Alignment(0))
		self.btnApp=QPushButton(i18n["ADD"])
		self.btnApp.setObjectName("btnFile")
		self.btnApp.setToolTip(i18n["EXECUTABLE_TOOLTIP"])
		self.btnApp.clicked.connect(self._addAction)
		hbox.addWidget(self.btnApp)
		box.addWidget(wdg,0,0,1,1,Qt.AlignCenter)
		#box.addWidget(QLabel(i18n["ICON"]),0,1,1,1)
		self.btnIcon=QPushButton()
		self.btnIcon.setObjectName("btnIcon")
		icn_desktop=QtGui.QIcon.fromTheme("shell")
		self.btnIcon.setIcon(icn_desktop)
		self.btnIcon.setIconSize(QSize(64,64))
		self.btnIcon.setToolTip(i18n["ICON_TOOLTIP"])
		self.btnIcon.clicked.connect(lambda:self._fileChooser(widget=self.btnIcon,path="/usr/share/icons",imgDialog=True))
		box.addWidget(self.btnIcon,1,1,2,1,Qt.AlignTop)
		box.addWidget(QLabel(i18n["NAME"]),1,0,1,1)
		self.inpName=QLineEdit()
		self.inpName.setPlaceholderText(i18n["NAME_PLACEHOLDER"])
		self.inpName.setToolTip(i18n["NAME_TOOLTIP"])
		self.inpName.setReadOnly(True)
		box.addWidget(self.inpName,2,0,1,1)
		lblApp=QLabel(i18n["DESCRIPTION"])
		box.addWidget(lblApp,3,0,1,1,Qt.AlignBottom)
		lblDesc=QLabel(_("Description (optional): "))
		self.inpDesc=QLineEdit()
		self.inpDesc.setPlaceholderText(_("Description"))
		self.inpDesc.setToolTip(_("Insert a description for the app"))
		self.inpDesc.setReadOnly(True)
		box.addWidget(self.inpDesc,4,0,1,2)
		self.hkBtn=QHotkeyButton(i18n["HOTKEY"],alternate=i18n["HOTKEY_PRESS"])
		self.hkBtn.pressed.connect(self._setHkText)
		box.addWidget(self.hkBtn,5,0,1,1,Qt.AlignLeft)
		btnOk=QPushButton("Ok")
		btnOk.clicked.connect(self._accepted)
		box.addWidget(btnOk,6,0,1,1,Qt.AlignRight)
		btnKo=QPushButton(i18n["CANCEL"])
		btnKo.clicked.connect(self.close)
		box.addWidget(btnKo,6,1,1,1,Qt.AlignRight)
		box.setRowStretch(0,1)
		box.setRowStretch(2,1)
		box.setRowStretch(3,1)
		box.setRowStretch(4,1)
		box.setRowStretch(6,2)
		self.setLayout(box)
	#def _loadScreen

	def _readScreen(self):
		self.action["Name"]=self.inpName.text()
		self.action["Comment"]=self.inpDesc.text()
		self.action["Icon"]=self.appIcon
		if len(self.fName)>0:
			self.action["fname"]=self.fName
	#def _readScreen

	def _accepted(self):
		if len(self.action)>0:
			self._readScreen()
			if self.cmbApp.currentText==i18n["EXECUTABLE"]:
				if self.action.get("type","")!="":
					self.showMsg("ERROR")
					self.close()
				elif self.action.get("type","")=="":
					self.action["type"]="desktop"
			self.accepted.emit(self.action)
		self.close()

	def _setHkText(self):
		self.hkBtn.setText(i18n["HOTKEY_PRESS"])

	def setParms(self,*args):
		if len(args)>0:
			action=args[0]
			self.inpName.setText(action.get("Name",""))
			self.inpDesc.setText(action.get("Comment",""))
			self.appIcon=action.get("Icon","")
			self.fName=action.get("fname",self.fName)
			if action.get("type")=="desktop":
				self.cmbApp.setCurrentText(i18n["EXECUTABLE"])
			else:
				self.cmbApp.setCurrentText(i18n["EFFECT"])
			self.action=action.copy()
	#def setParms

	def _addAction(self):
		self.parent.setCurrentStack(1,parms=self.cmbApp.currentText())
	#def _addAction(self):

	def _fileChooser(self,widget=None,path=None,imgDialog=None):
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		if imgDialog:
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
		else:
			fdia.setNameFilter(_("All files(*.*)"))
		if path:
			self._debug("Set path to %s"%path)
			fdia.setDirectory(path)
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			if widget:
				if imgDialog:
					self.appIcon=fdia.selectedFiles()[0]
					icn=QtGui.QIcon(self.appIcon)
					widget.setIcon(icn)
				else:
					widget.setText(fchoosed)
			self.force_change=True
			self.setChanged(True)
			return(fchoosed)
	#def _fileChooser

	def updateScreen(self):
		icn=QtGui.QIcon.fromTheme(self.appIcon)
		self.btnIcon.setIcon(icn)
	#def updateScreen
#class portrait(QStackedWindowItem):

class launchers(QStackedWindow):
	accepted=Signal("PyObject")
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.disableNavBar(True)
		self._debug("confDesktops Load")
		home=os.environ['HOME']
		self.appIcon='shell'
		self.icon=('org.kde.plasma.quicklaunch')
		self.tooltip=(_("From here you can add a custom launcher"))
		self.desktopPaths=["/usr/share/applications",os.path.join(os.environ.get("USER"),".local","share","applications")]
		self.destPath=""
		self.app2menu=App2Menu.app2menu()
		p=portrait()
		p.accepted.connect(self._accepted)
		self.addStack(p)
		self.addStack(actionSelector())
	#def __init__

	def _accepted(self,*args):
		if len(args)>0 and len(self.destPath)>0:
			action=args[0]
			if os.path.exists(self.destPath)==False:
				os.makedirs(self.destPath)
			if action.get("type")=="desktop":
				self._addDesktop(action)
			if action.get("type")=="effect":
				self._addEffect(action)
			if action.get("type")=="script":
				self._addScript(action)
		self.accepted.emit(args)
		self.close()

	def _addEffect(self,action):
		fname=action.get("fname","")
		if fname=="":
			prefix="{}".format(len(os.listdir(self.destPath))).zfill(3)
			fname="{}_{}.desktop".format(prefix,action.get("Exec"))
			fname=os.path.join(self.destPath,fname)
		desktop="[Desktop Entry]\nEncoding=UTF-8\n"
		desktop+="Name={}\n".format(action.get("Name"))
		desktop+="Comment={}\n".format(action.get("Comment"))
		desktop+="Icon={}\n".format(action.get("Icon"))
		cmd="qdbus org.kde.KWin /Effects org.kde.kwin.Effects.toggleEffect {}".format(action.get("Exec"))
		desktop+="Exec={}\n".format(cmd)
		with open(fname,"w") as f:
			f.write(desktop)
	#def _addEffect

	def _addScript(self,action):
		fname=action.get("fname","")
		if fname=="":
			prefix="{}".format(len(os.listdir(self.destPath))).zfill(3)
			fname="{}_{}.desktop".format(prefix,action.get("Exec"))
			fname=os.path.join(self.destPath,fname)
		desktop="[Desktop Entry]\nEncoding=UTF-8\n"
		desktop+="Name={}\n".format(action.get("Name"))
		desktop+="Comment={}\n".format(action.get("Comment"))
		desktop+="Icon={}\n".format(action.get("Icon"))
		cmd="{0}/loadScript.sh {1} add".format(os.path.basename(self.destPath),action.get("Exec"))
		desktop+="Exec={}\n".format(cmd)
		fname=os.path.join(self.destPath,fname)
		with open(fname,"w") as f:
			f.write(desktop)
	#def _addEffect

	def _addDesktop(self,action):
		fdesktop=action.get("Path","")
		fname=action.get("fname","")
		app=self.app2menu.init_desktop_file()
		if fname=="":
			prefix="{}".format(len(os.listdir(self.destPath))).zfill(3)
			fname="{}_{}.desktop".format(prefix,os.path.basename(action.get("Exec")).lower().replace(" ","_").replace("%",""))
			fname=os.path.join(self.destPath,fname)
			action["fname"]=fname
		if fdesktop!="":
			app=self.app2menu.get_desktop_info(fdesktop)
		app.update(action)
		fname=action.get("fname","")
		if os.path.exists(fname) and len(fname)>0:
			os.unlink(fname)
		fname=app.get("fname","")
		self.app2menu.write_custom_desktop(app,fname)
		return

		desktop="[Desktop Entry]\nEncoding=UTF-8\n"
		desktop+="Name={}\n".format(action.get("Name"))
		desktop+="Comment={}\n".format(action.get("Comment"))
		desktop+="Icon={}\n".format(action.get("Icon"))
		cmd="{0}/loadScript.sh {1} add".format(os.path.basename(self.destPath),action.get("Exec"))
		desktop+="Exec={}\n".format(cmd)
		fname=os.path.join(self.destPath,fname)
		with open(fname,"w") as f:
			f.write(desktop)





		fname=action.get("fname","")
		fdesktop=action.get("Path","")
		if fname.strip()=="":
			prefix="{}".format(len(os.listdir(self.destPath))).zfill(3)
			fname="{}_{}.desktop".format(prefix,os.path.basename(action.get("Exec").lower().split()[0]))
			fname=os.path.join(self.destPath,fname)
		if len(fdesktop)>0:
			prefix="{}".format(len(os.listdir(self.destPath))).zfill(3)
			shutil.copy(fdesktop,fname)
			self._debug("Copy {} -> {}".format(fdesktop,fname))
		else: #Edit
			app=self.app2menu.get_desktop_info(fname)
	#def _addDesktop

	def setParms(self,action):
		actionPath=os.path.join(self.destPath,action)
		actionData=self.app2menu.get_desktop_info(actionPath)
		actionData["type"]="desktop"
		if actionData["Exec"].startswith("qdbus"):
			actionData["type"]="effect"
		elif "loadScript.sh" in actionData["Exec"]:
			actionData["type"]="script"
		actionData["fname"]=actionPath
		self.setCurrentStack(0,parms=actionData)
	#def setParms
		
	def _debug(self,msg):
		if self.dbg:
			print("ConfDesktops: %s"%msg)
	#def _debug

if __name__=="__main__":
	app=QApplication(["Add launcher"])
	mw=launchers()
	mw.show()
	app.exec_()