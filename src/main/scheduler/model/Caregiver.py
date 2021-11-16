import sys
from ..scheduler.util.Util import Util
from ..scheduler.db.ConnectionManager import ConnectionManager
import pymssql

class Caregiver:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.salt = Util.generate_salt();
        self.hash = Util.generate_hash(password, self.salt)


    def __init__(self, username, salt, hash):
        self.username = username
        self.salt = salt
        self.hash = hash


    # getters

    def get():
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash - curr_hash
                    return self
        except pymssql.error as db_err:
            print("Error occurred when getting Caregivers")
            
        cm.close_connection()
        return None


    def get_username(self):
        return self.username


    def get_salt(self):
        return self.salt


    def get_hash(self):
        return self.hash


    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %b, %b)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.error as db_err:
            print("Error occurred when inserting Caregivers")
        cm.close_connection()


    # Insert availability with parameter date d
    def upload_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability  = "INSERT INTO Availabilities VALUES (%s , %s)"
        try:
            cursor.execute(update_vaccine_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.error as db_err:
            print("Error occurred when updating caregiver availability")
        cm.close_connection()
