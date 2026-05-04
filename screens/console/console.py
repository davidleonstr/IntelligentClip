import QFlow
from QFlow.modules import config, session
from QFlow.helpers import Icon

from config import CONFIG
from helpers.builders import Object

from qtpy.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit
)

from app import RELATIVES

import sys
import io

from .highlighter import PythonHighlighter
from .utilities import Utilities

SCREENCONFIG = Object(
    CONFIG.language(
        name='console', language=RELATIVES.LANGUAGE, objType='screens'
    )
).obj

@QFlow.screen(
    name='console',
    parentType=QFlow.App
)
@config(SCREENCONFIG)
@session()
class ConsoleScreen(QFlow.Screen):
    def __init__(self, parent):
        self.args['parent'] = parent
        super().__init__(**self.args)

        self.utilities = Utilities()

    def UI(self):        
        self.screenLayout = QVBoxLayout()
        self.screenLayout.setContentsMargins(30, 20, 30, 10)

        self.nav = QHBoxLayout()

        self.logo = QLabel()
        logoPixmap = Icon(CONFIG.tree('icons', 'files', 'normals', 'app-icon'), 42, 42)
        self.logo.setPixmap(logoPixmap)

        self.title = QLabel(self.Config.texts.labels.title)
        self.title.setObjectName('title')

        self.content = QHBoxLayout()
        self.content.setSpacing(0)
        self.content.setContentsMargins(0, 20, 0, 20)

        self.bottom = QHBoxLayout()
        self.bottom.setSpacing(20)

        self.nav.addWidget(self.logo)
        self.nav.addSpacing(10)
        self.nav.addWidget(self.title)
        self.nav.addStretch()

        self.consoleOutput = QTextEdit()
        self.consoleOutput.setReadOnly(True)
        self.outputLabel = QLabel(self.Config.texts.labels.outputText)

        self.outputLayout = QVBoxLayout()
        self.outputLayout.setSpacing(10)
        self.outputLayout.addWidget(self.outputLabel)
        self.outputLayout.addWidget(self.consoleOutput)

        self.consoleInput = QTextEdit()
        self.consoleInputHighlighter = PythonHighlighter(self.consoleInput.document())

        self.inputLabel = QLabel(self.Config.texts.labels.inputCode)

        self.inputLayout = QVBoxLayout()
        self.inputLayout.setSpacing(10)
        self.inputLayout.addWidget(self.inputLabel)
        self.inputLayout.addWidget(self.consoleInput)

        self.runButton = QPushButton(self.Config.texts.buttons.runCode)
        self.runButton.clicked.connect(self.runCode)
        self.runButton.setObjectName('resetButton')

        self.backButton = QPushButton(self.Config.texts.buttons.goBack)
        self.backButton.setObjectName('normalButton')
        self.backButton.clicked.connect(self.parent().goBack)

        self.content.addLayout(self.outputLayout)
        self.content.addLayout(self.inputLayout)

        self.bottom.addWidget(self.runButton)
        self.bottom.addWidget(self.backButton)
        self.bottom.addStretch(1) 

        self.screenLayout.addLayout(self.nav)
        self.screenLayout.addLayout(self.content)
        self.screenLayout.addLayout(self.bottom)

        self.setLayout(self.screenLayout)

        self.loadDefaultDebugCode()
    
    def writeOutput(self, text: str):
        self.consoleOutput.setReadOnly(False)
        self.consoleOutput.setText(text)
        self.consoleOutput.setReadOnly(True)
    
    def runCode(self):
        output = None

        try:
            buffer = io.StringIO()
            stdout = sys.stdout
            sys.stdout = buffer

            exec(self.consoleInput.toPlainText())

            sys.stdout = stdout
            output = buffer.getvalue()            
        except Exception as e:
            output = str(e)
        
        self.writeOutput(output)
    
    def loadDefaultDebugCode(self):
        try:
            code = open(
                'screens/console/defaultDebugCode.txt', encoding='utf-8'
            ).read()
        except:
            code = ''
            
        self.consoleInput.setText(code)