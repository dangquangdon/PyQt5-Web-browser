import json
import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QImage, QWindow, QKeySequence
from PyQt5.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QStackedLayout, QTabBar,
                             QVBoxLayout, QWidget, QShortcut, QKeySequenceEdit)
from PyQt5.QtWebEngineWidgets import *


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()


class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")
        self.setMinimumSize(800, 600)
        self.create_app()
        self.setWindowIcon(QIcon('./logo.png'))

    def create_app(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Tabs
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.closeTab)
        self.tabbar.tabBarClicked.connect(self.switchTab)

        self.tabbar.setCurrentIndex(0)

        # Shortcut Key
        self.shortcutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewTab.activated.connect(self.addTab)

        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutReload.activated.connect(self.reloadPage)

        # Keep track of the tabs
        self.tabCount = 0
        self.tabs = []

        # Create Address Bar
        self.toolBar = QWidget()
        self.toolBarLayout = QHBoxLayout()

        self.addressbar = AddressBar()
        self.addressbar.returnPressed.connect(self.browseTo)

        # new tab button
        self.newTabButton = QPushButton("+")
        self.newTabButton.clicked.connect(self.addTab)

        # Set toolbar button
        self.BackButton = QPushButton("<<")
        self.ForwardButton = QPushButton(">>")
        self.BackButton.clicked.connect(self.goBackward)
        self.ForwardButton.clicked.connect(self.goForward)

        self.ReloadButton = QPushButton("Reload")
        self.ReloadButton.clicked.connect(self.reloadPage)

        # Build Toolbar
        self.toolBar.setObjectName("Toolbar")
        self.toolBar.setLayout(self.toolBarLayout)
        self.toolBarLayout.addWidget(self.BackButton)
        self.toolBarLayout.addWidget(self.ForwardButton)
        self.toolBarLayout.addWidget(self.ReloadButton)
        self.toolBarLayout.addWidget(self.addressbar)
        self.toolBarLayout.addWidget(self.newTabButton)

        # set main view
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        # Add Widgets
        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)
        self.addTab()

        self.show()

    # The connection will sent the index of the tab that is clicked
    def closeTab(self, ind):
        self.tabbar.removeTab(ind)

    def addTab(self):
        ind = self.tabCount
        self.tabs.append(QWidget())
        self.tabs[ind].layout = QVBoxLayout()
        self.tabs[ind].layout.setContentsMargins(0, 0, 0, 0)

        # For tab switching
        self.tabs[ind].setObjectName("tab" + str(ind))

        self.tabs[ind].content = QWebEngineView()
        self.tabs[ind].content.load(QUrl.fromUserInput("http://google.com"))

        self.tabs[ind].content.titleChanged.connect(
            lambda: self.set_tab_content(ind, 'title'))
        self.tabs[ind].content.iconChanged.connect(
            lambda: self.set_tab_content(ind, 'icon'))
        self.tabs[ind].content.urlChanged.connect(
            lambda: self.set_tab_content(ind, "url"))

        # Add webview to tabs layout
        self.tabs[ind].layout.addWidget(self.tabs[ind].content)

        # set top level tab from list to layout
        self.tabs[ind].setLayout(self.tabs[ind].layout)

        # Add tab to top level
        self.container.layout.addWidget(self.tabs[ind])
        self.container.layout.setCurrentWidget(self.tabs[ind])

        # Set the tab at top of the screen
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(
            ind, {"object": "tab" + str(ind), "initial": ind})
        self.tabbar.setCurrentIndex(ind)

        self.tabCount += 1

    def switchTab(self, i):
        tab_data = self.tabbar.tabData(i)['object']
        tab_content = self.findChild(QWidget, tab_data)
        self.container.layout.setCurrentWidget(tab_content)

        newUrl = tab_content.content.url().toString()
        self.addressbar.setText(newUrl)

    def browseTo(self):
        text = self.addressbar.text()

        # Get the index number of the current tab
        i = self.tabbar.currentIndex()
        # Get the name of the current tab
        tab = self.tabbar.tabData(i)['object']
        # Get the webview
        wv = self.findChild(QWidget, tab).content
        if "http" not in text:
            if "." not in text:
                url = "https://www.google.com/#q=" + text
            else:
                url = "https://" + text
        else:
            url = text
        wv.load(QUrl.fromUserInput(url))

    def set_tab_content(self, i, type):
        """
            self.tabs[i].objectName => tab1
            self.tabs[i].tabData(i)['object'] => tab1
        """

        tab_objectName = self.tabs[i].objectName()

        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())['object']

        if current_tab == tab_objectName and type == "url":
            newUrl = self.findChild(
                QWidget, tab_objectName).content.url().toString()
            self.addressbar.setText(newUrl)
            return False

        count = 0
        running = True

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count >= 99:
                running = False

            if tab_objectName == tab_data_name['object']:
                if type == 'title':
                    new_title = self.findChild(
                        QWidget, tab_objectName).content.title()
                    self.tabbar.setTabText(count, new_title)
                elif type == 'icon':
                    newIcon = self.findChild(
                        QWidget, tab_objectName).content.icon()
                    self.tabbar.setTabIcon(count, newIcon)

                running = False
            else:
                count += 1

    def goBackward(self):
        activeTabIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeTabIndex)['object']
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def goForward(self):
        activeTabIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeTabIndex)['object']
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def reloadPage(self):
        activeTabIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeTabIndex)['object']
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set Environment variables
    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '667'

    # Set stylesheet
    with open('style.css', "r") as style:
        app.setStyleSheet(style.read())

    window = App()
    sys.exit(app.exec_())
