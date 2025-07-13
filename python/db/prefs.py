import sqlite3
import os
from .utils import DB


class Prefs:
    """
        Prefs class used to configure everything.  Use this to store magic numbers,
        meta parameters, etc.
    """
    def __init__ (self):
        self._preferences = dict()
        for row in DB.select("select key, value from preferences", ()):
            self._preferences[row[0]] = row[1]
        
    def get (pref,default=None):
        if pref not in self._preferences:
            value = input ("Unknown preference. Please input value [{default}]:")
            set(pref,value)
        return self._preferences[pref]

    def set (pref,value):
        DB.commit ("DELETE FROM preferences WHERE key = ?",(pref,))
        DB.commit ("INSERT INTO preferences (key,value) VALUES ( ? , ?)", (pref,value))
        self._preferences[pref] = value
