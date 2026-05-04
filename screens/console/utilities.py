import ctypes

class Utilities:
    @staticmethod
    def getObjById(objId):
        return ctypes.cast(objId, ctypes.py_object).value

    @staticmethod
    def listObjMethods(obj):
        return [x for x in dir(obj) if callable(getattr(obj, x))]

    @staticmethod
    def listObjProperties(obj):
        return [x for x in dir(obj) if not callable(getattr(obj, x))]