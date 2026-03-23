import QFlow
from QFlow.modules import session

from qtpy.QtWidgets import (
    QVBoxLayout
)
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
import os

@QFlow.screen(
    name='error',
    parentType=QFlow.App
)
@session()
class ErrorScreen(QFlow.Screen):
    def __init__(self, parent):
        self.args['parent'] = parent
        super().__init__(**self.args)

    def UI(self):
        # Create screen layout
        self.screenlayout = QVBoxLayout()

        # Init brower
        self.browser = QWebEngineView()
        # Set screen
        path = os.path.abspath('screens/html/error-screen.html')
        self.browser.setUrl(QUrl.fromLocalFile(path))

        # Add browser
        self.screenlayout.addWidget(self.browser)

        # Set layour
        self.setLayout(self.screenlayout)