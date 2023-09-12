from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
# regular expressions for ensure password
import re

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None
current_caregiver = None

def strongPassword(password):
    strong = False
    if len(password) < 8:
        print("Make sure your password is at lest 8 letters")
    elif re.search("[0-9]", password) is None:
        print("Make sure your password has number in it")
    elif re.search("[a-z]", password) is None: 
        print("Make sure your password has letter in it")
    elif re.search("[A-Z]", password) is None: 
        print("Make sure your password has capital letter in it")
    elif re.search("[!|@|#|\?]", password) is None: 
        print("Make sure your password has special character, from “!”, “@”, “#”, “?”")
    else:
        strong = True
        print("Your password seems fine")
    return strong

def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user. Input is Invalid")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return
    # check 3: check if the password is strong enough
    if not strongPassword(password):
        print(password)
        print("Try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created patient user ", username)

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    # check 3: check if the password is strong enough
    if not strongPassword(password):
        print("Try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def login_patient(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient

def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver

def search_caregiver_schedule(tokens):
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print("Invalid input, please try again!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    ava_date = tokens[1]
    get_availability = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    get_vaccines = "SELECT * FROM Vaccines"
    
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_availability, ava_date)
        caregiver_result = cursor.fetchall()
        if not caregiver_result:
            print("No caregiver available for given day.")
        else:
            print("Available caregivers are: ")
            caregivers = ""
            for row in caregiver_result:
                caregivers += row["Username"] + " "
            print(caregivers + "\n")
            print("Vaccines availability:")

            cursor.execute(get_vaccines)
            vaccines_result = cursor.fetchall()
            if not vaccines_result:
                print("No vaccines available")
            else:
                for row in vaccines_result:
                    print("Vaccine: " + row['Name'] + ", " + 
                    "Availablility: " + str(row['Doses']))
    
    except pymssql.Error as e:
        print("Error occurred when getting availability of caregiver or vaccines, please try again")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred, please try again")
        print("Error:", e)
    finally:
        cm.close_connection()

def reserve(tokens):
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    elif current_caregiver is not None:
        print("Please login as a patient!")
        return
    if len(tokens) != 3:
        print("Invalid input, please try again!")
        return

    cm1 = ConnectionManager()
    conn1 = cm1.create_connection()
    cm2 = ConnectionManager()
    conn2 = cm2.create_connection()
    
    # cursor for update db
    cm_update = ConnectionManager()
    conn_update = cm_update.create_connection()
    cursor_update = conn_update.cursor()

    app_date = tokens[1]
    app_vaccine = tokens[2].lower()
    availability = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    vaccines = "SELECT * FROM Vaccines WHERE Name = %s"
    update_app_sql = "INSERT INTO Appointments VALUES (%s , %s, %s , %s, %s)"
    update_ava_sql = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
    update_vacc_sql = "UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = %s"

    try:
        cursor1 = conn1.cursor(as_dict=True)
        cursor1.execute(availability, app_date)
        ava_list = cursor1.fetchall()
        
        cursor2 = conn2.cursor(as_dict=True)
        cursor2.execute(vaccines, app_vaccine)
        ava_vaccines_list = cursor2.fetchall()

        # Get vaccine doses information if vaccine exist. For checking if givin vaccine is availabe.
        doses = ava_vaccines_list[0]["Doses"]
    
        if not ava_list:
            print("No Caregiver is avaible!")
        elif not ava_vaccines_list:
            print("No such vaccine.")
        elif doses == 0:
            print("Not enough available doses!")
        else:
            # git first people in the list
            caregiver = ava_list[0]["Username"]
            appointment_id = current_patient.get_username() + "_" + caregiver + "_" + app_date
            cursor_update.execute(update_app_sql, (appointment_id, app_date, 
                           current_patient.get_username(), caregiver,
                           app_vaccine))
            conn_update.commit()
            cursor_update.execute(update_ava_sql, (app_date, caregiver))
            conn_update.commit()
            cursor_update.execute(update_vacc_sql, app_vaccine)
            conn_update.commit()
            print(f"Successfully make appointment, here is information:\
                  \nAppointment ID: {appointment_id}, Caregiver username: {caregiver}")

    except pymssql.Error as e:
        print("Error occurred, please try again")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred, please try again")
        print("Error:", e)
    finally:
        cm1.close_connection()
        cm2.close_connection()
        cm_update.close_connection()

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")

def cancel(tokens):
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return                                                                          
    if len(tokens) != 2:
        print("Invalid input, please try again!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    app_id = tokens[1]

    get_app_sql = "SELECT * FROM Appointments WHERE appID = %s"
    update_app_sql = "DELETE FROM Appointments WHERE appID = %s"
    update_ava_sql = "INSERT INTO Availabilities VALUES (%s, %s)"
    update_vacc_sql = "UPDATE Vaccines SET Doses = Doses + 1 WHERE Name = %s"

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_app_sql, app_id)
        app_list = cursor.fetchall()

        if not app_list:
            print("No appointment for gevin appointment id, please try again")
        else:
            time = app_list[0]["Time"]
            caregiver = app_list[0]["caregiver_name"]
            vaccine = app_list[0]["vaccine_name"]

            cursor.execute(update_app_sql, app_id)
            conn.commit()
            cursor.execute(update_ava_sql, (time, caregiver))
            conn.commit()
            cursor.execute(update_vacc_sql, vaccine)
            conn.commit()
            print(f"Successfully cancel appointment: {app_id}")
    
    except pymssql.Error as e:
        print("Error occurred, please try again")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred, please try again")
        print("Error:", e)
    finally:
        cm.close_connection()

def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1].lower()
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")

def show_appointments(tokens):
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    if len(tokens) != 1:
        print("Invalid input, Please try again!")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    patient_check = "SELECT appID, Time, vaccine_name, caregiver_name FROM Appointments WHERE patient_name = %s ORDER BY appID"
    caregiver_check = "SELECT appID, Time, vaccine_name, patient_name FROM Appointments WHERE caregiver_name = %s ORDER BY appID"

    try:
        cursor = conn.cursor(as_dict=True)
        if current_patient is not None:
            cursor.execute(patient_check, current_patient.get_username())
            patient_appointment_view = cursor.fetchall()
            if not patient_appointment_view:
                print("No appointment yet")
            else:
                for row in patient_appointment_view:
                    print(f"appointment id: {row['appID']},",
                          f"time of appointment: {row['Time'].strftime('%m/%d/%Y')}, ",
                          f"vaccine: {row['vaccine_name']}, ",
                          f"caregiver name: {row['caregiver_name']}")
        else:
            cursor.execute(caregiver_check, current_caregiver.get_username())
            caregiver_appointment_view = cursor.fetchall()
            if not caregiver_appointment_view:
                print("No appointment yet")
            else:
                for row in caregiver_appointment_view:
                    print(f"appointment id: {row['appID']},",
                          f"time of appointment: {row['Time'].strftime('%m/%d/%Y')}, ",
                          f"vaccine: {row['vaccine_name']}, ",
                          f"caregiver name: {row['patient_name']}")
    except pymssql.Error as e:
        print("Error occurred, please try again")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred, please try again")
        print("Error:", e)
    finally:
        cm.close_connection()

def logout(tokens):
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    else:
        try:
            current_patient = None
            current_caregiver = None
            print("Successfully logged out!")
        except:
            print("Some error appear, Please try again!")

def commands():
    print()
    print(" *** Please enter one of the following commands (Input value are case sensitive expect vaccine name)*** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
def start():
    stop = False
    commands()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break
        
        # I remove the to lower because it will change the password to lowercase,
        # and I think is not necessary for most of them. I will ignore vaccine and operation case.
        # ignore vaccine case in function.
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        operation = operation.lower()
        if operation == "create_patient":
            create_patient(tokens)
            commands()
        elif operation == "create_caregiver":
            create_caregiver(tokens)
            commands()
        elif operation == "login_patient":
            login_patient(tokens)
            commands()
        elif operation == "login_caregiver":
            login_caregiver(tokens)
            commands()
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
            commands()
        elif operation == "reserve":
            reserve(tokens)
            commands()
        elif operation == "upload_availability":
            upload_availability(tokens)
            commands()
        elif operation == "cancel":
            cancel(tokens)
            commands()
        elif operation == "add_doses":
            add_doses(tokens)
            commands()
        elif operation == "show_appointments":
            show_appointments(tokens)
            commands()
        elif operation == "logout":
            logout(tokens)
            commands()
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")

if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")
    start()
