import sqlite3   
import csv       


DB_FILE="info.db"

db = sqlite3.connect(DB_FILE) 
c = db.cursor()


def populate