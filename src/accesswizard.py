#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication
from QtExtraWidgets import QStackedWindow
import gettext
gettext.textdomain('accesswizard')
_ = gettext.gettext
app=QApplication(["Access Wizard"])
config=QStackedWindow()
if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
config.addStacksFromFolder(os.path.join(abspath,"stacks"))
config.setBanner(os.path.join(os.path.dirname(__file__),"rsrc","accesswizard_banner.png"))
config.setWiki("https://wiki.edu.gva.es/lliurex/tiki-index.php?page=accesswizard")
config.setIcon("accesswizard")
config.show()
config.setMinimumWidth(config.sizeHint().width()*1.9)
config.setMinimumHeight(config.sizeHint().width())
app.exec()
