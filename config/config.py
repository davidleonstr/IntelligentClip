from helpers.files import JSON
from helpers.builders import Folder
import os

class Config:
    def __init__(self):
        self.ConfigFile= JSON(r'config/config.json')
        'Global configuration file.'

        self.CONFIG = self.ConfigFile.read()
        'Global configuration dict.'

        self.folders = {
            'styles': Config.getFolderFiles(
                Folder(self.CONFIG['app']['folders']['styles']).listFiles()
            ),
            'configs': {
                'windows': Config.getFolderFiles(
                    Folder(
                        self.getConfigsPath(
                            self.CONFIG['app']['folders']['configs']['windows']
                        )
                    ).listFiles()
                ),
                'screens': Config.getFolderFiles(
                    Folder(
                        self.getConfigsPath(
                            self.CONFIG['app']['folders']['configs']['screens']
                        )
                    ).listFiles()
                )
            },
            'locales': {
                'path': self.CONFIG['app']['folders']['locales']['path'],
                'base': {
                    'windows': self.CONFIG['app']['folders']['locales']['base']['windows'],
                    'screens': self.CONFIG['app']['folders']['locales']['base']['screens']
                },
                'languages': {}
            },
            'icons': {
                'notifications': Config.getFolderFiles(
                    Folder(
                        self.getIconsPath(
                            self.CONFIG['app']['folders']['icons']['notifications']
                        )
                    ).listFiles()
                ),
                'normals': Config.getFolderFiles(
                    Folder(
                        self.getIconsPath(
                            self.CONFIG['app']['folders']['icons']['normals']
                        )
                    ).listFiles()
                ),
                'labels': Config.getFolderFiles(
                    Folder(
                        self.getIconsPath(
                            self.CONFIG['app']['folders']['icons']['labels']
                        )
                    ).listFiles()
                )
            }
        }
        'Dict that contains global styles and configurations of windows and screens.'

        self.loadLocales()

    def loadLocales(self) -> None:
        languages = Folder(self.folders['locales']['path']).listFolders()

        bases: dict = self.folders['locales']['base']
        path: str = self.folders['locales']['path']

        for language in languages:
            self.folders['locales']['languages'][language] = {}
            
            for key, value in bases.items():
                items = Config.getFolderFiles(
                    Folder(
                        f'{path}{language}{value}'
                    ).listFiles()
                )

                self.folders['locales']['languages'][language][key] = items
    
    def getFolderFiles(items: list) -> dict:
        files = {}

        for item in items:
            item: str
            name, _ = os.path.splitext(os.path.basename(item))

            files[name] = item

        return files

    def getIconsPath(self, folder: str) -> str:
        return self.CONFIG['app']['folders']['icons']['path'] + folder

    def getConfigsPath(self, folder: str) -> str:
        return self.CONFIG['app']['folders']['configs']['path'] + folder

CONFIG = Config()
'Application Inherent Configuration.'