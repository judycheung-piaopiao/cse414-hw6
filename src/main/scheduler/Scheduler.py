import re

from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    if len(tokens)!=3:
        print("Error creating patient")
        start()
        return
    username=tokens[1]
    password=tokens[2]
    if username_exists_patient(username):
        print("Username taken, try again")
        start()
        return

    if len(password)<8:
        print("Please enter a password of at least 8 characters")
        start()
        return
    if not re.search(r'[A-Z]', password):
        print("Password must contain at least one uppercase letter!")
        start()
        return

    if not re.search(r'[a-z]', password):
        print("Password must contain at least one lowercase letter!")
        start()
        return

    if not re.search(r'[0-9]',password):
        print("Please enter a password of at least one number!")
        start()
        return
    if not re.search(r'[!@#?]',password):
        print("Please enter a password of at least one special character!")
        start()
        return

    salt=Util.generate_salt()
    hash=Util.generate_hash(password,salt)
    patient=Patient(username=username,salt=salt,hash=hash)
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Create patient failed")
        print("Error:", e)
        quit()
    except Exception as e:
        print("Create patient failed")
        print("Error:", e)
        quit()
    print("Created user", username)
    start()


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patient WHERE Username = %s"
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
    if len(password)<8:
        print("Please enter a password of at least 8 characters")
        start()
        return
    if not re.search(r'[A-Z]', password):
        print("Password must contain at least one uppercase letter!")
        start()
        return

    if not re.search(r'[a-z]', password):
        print("Password must contain at least one lowercase letter!")
        start()
        return

    if not re.search(r'[0-9]',password):
        print("Please enter a password of at least one number!")
        start()
        return
    if not re.search(r'[!@#?]',password):
        print("Please enter a password of at least one special character!")
        start()
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
    """
    TODO: Part 1
    """
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
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
        print("Login patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login patient failed")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as: " + username)
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
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    if len(tokens) != 2:
        print("Please try again!")
        start()
        return
    split_date=tokens[1].split("-")
    if len(split_date) != 3:
        print("Please try again!")
        start()
        return
    if len(split_date[0]) != 2:
        print("Please try again!")
        start()
        return
    if len(split_date[1]) != 2:
        print("Please try again!")
        start()
        return
    if len(split_date[2]) != 4:
        print("Please try again!")
        start()
        return

    month=int(split_date[0])
    day=int(split_date[1])
    year=int(split_date[2])

    if month==00 or day==00 or year==0000:
        print("Please try again!")
        start()
        return
    if day>31 or month>12:
        print("Please try again!")
        start()
        return
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        start()
        return

    #find available caregiver
    res_str=""
    cm=ConnectionManager()
    conn = cm.create_connection()
    cursor=conn.cursor(as_dict=True)
    find_caregiver_for_date="select Username from Availabilities where Time=%s order by Username asc"
    try:
        d=datetime.datetime(year,month,day)
        cursor.execute(find_caregiver_for_date,d)
        result=cursor.fetchall()
        if len(result) != 0:
            for row in result:
                res_str=res_str+row['Username']+" "
            print(res_str)
        else:
            print("Please try again!")
        cm.close_connection()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()

    #find available vaccines
    cm=ConnectionManager()
    conn = cm.create_connection()
    cursor=conn.cursor(as_dict=True)
    find_vaccine="select * from Vaccines"
    try:
        cursor.execute(find_vaccine)
        v_result=cursor.fetchall()
        if len(v_result) != 0:
            for row in v_result:
                print(row['Name'],row['Doses'])
        else:
            print("Please try again!")
        cm.close_connection()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
    start()



def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver is not None:
        print("Please login as a patient!")
        start()
        return
    if current_patient is None:
        print("Please login first!")
        start()
        return
    if len(tokens) != 3:
        print("Please try again! len(tokens) != 3")
        start()
        return
    date=tokens[1]
    vaccine=tokens[2]
    split_date=date.split("-")

    if len(split_date) != 3:
        print("Please try again!")
        start()
        return

    if len(split_date[0]) != 2:
        print("Please try again!")
        start()
        return
    if len(split_date[1]) != 2:
        print("Please try again!")
        start()
        return
    if len(split_date[2]) != 4:
        print("Please try again!")
        start()
        return

    month = int(split_date[0])
    day = int(split_date[1])
    year = int(split_date[2])

    if month == 00 or day == 00 or year == 0000:
        print("Please try again!")
        start()
        return
    if day > 31 or month > 12:
        print("Please try again!")
        start()
        return

    #check available caregivers
    cm=ConnectionManager()
    conn = cm.create_connection()
    cursor=conn.cursor(as_dict=True)
    find_caregiver_for_date="select Username from Availabilities where Time=%s order by Username asc"
    try:
        d=datetime.datetime(year,month,day)
        cursor.execute(find_caregiver_for_date,d)
        result=cursor.fetchall()
        if len(result) != 0:
            caregiver=[row['Username'] for row in result]
            book_caregiver=caregiver[0]
        else:
            print("No caregiver is available!")
            cm.close_connection()
            start()
            return
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    cm.close_connection()

    #check if vaccine is available
    cm=ConnectionManager()
    conn = cm.create_connection()
    cursor=conn.cursor()
    find_vaccine="select Name,Doses from Vaccines where Name=%s"
    try:
        cursor.execute(find_vaccine,vaccine)
        v_result=cursor.fetchall()
        if len(v_result)==0:
            print("Not enough available doses!")
            cm.close_connection()
            start()
            return
        for row in v_result:
            available_doses=row[1]
            if available_doses>0:
                available_doses-=1
                update_doses="update Vaccines set Doses=%d where Name=%s"
                cursor.execute(update_doses,(available_doses,vaccine))
                conn.commit()
                print("Updated available doses!")
            else:
                print("No available doses!")
                cm.close_connection()
                start()
                return
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    cm.close_connection()

    #remove caregiver's availability
    cm=ConnectionManager()
    conn = cm.create_connection()
    cursor=conn.cursor()
    remove_caregiver="delete from Availabilities where Time=%s and Username=%s"
    try:
        cursor.execute(remove_caregiver,(d,book_caregiver))
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    cm.close_connection()

    #add appointment
    cm=ConnectionManager()
    conn = cm.create_connection()
    cursor=conn.cursor()
    appoint_id="select max(ID) from Appointments"
    try:
        cursor.execute(appoint_id)
        result=cursor.fetchall()
        if result[0][0] is None:
            id=1
        else:
            id=int(result[0][0])+1
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    add_appoint="insert into Appointments values(%d,%s,%s,%s,%s)"
    try:
        cursor.execute(add_appoint, (id,d,current_patient.username,book_caregiver,vaccine))
        print("Appointment ID "+str(id)+", Caregiver username "+str(book_caregiver))
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
    cm.close_connection()
    start()



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
    """
    TODO: Extra Credit
    """
    global current_caregiver
    global current_patient
    if len(tokens) != 2:
        print("Please try again!")
        start()
        return
    if current_caregiver is None and current_patient is None:
        print("Log in first!")
        start()
        return

    appoint_id=tokens[1]
    cm=ConnectionManager()
    conn = cm.create_connection()
    cursor=conn.cursor()
    find_appoint="select * from Appointments where ID=%s"
    try:
        cursor.execute(find_appoint,appoint_id)
        result=cursor.fetchall()
        if len(result) != 0:
            for row in result:
                app_date=row[1]
                app_patient=row[2]
                app_caregiver=row[3]
                app_vaccine=row[4]
                delete_appoint="delete from Appointments where ID=%s"
                try:
                    cursor.execute(delete_appoint,appoint_id)
                    conn.commit()
                except pymssql.Error:
                    print("Please try again!")
                    cm.close_connection()
                    start()
                    return
                cm.close_connection()

                #return the vaccine into available vaccine
                cm=ConnectionManager()
                conn = cm.create_connection()
                cursor=conn.cursor()
                return_vac="update Vaccines set Doses=Doses+1 where Name=%s"
                try:
                    cursor.execute(return_vac,app_vaccine)
                    conn.commit()
                except pymssql.Error:
                    print("Please try again!")
                    cm.close_connection()
                    start()
                    return
                cm.close_connection()

                #return caregiver's availability
                cm=ConnectionManager()
                conn = cm.create_connection()
                cursor=conn.cursor()
                return_avai="insert into Availabilities values (%s,%s)"
                try:
                    cursor.execute(return_avai,(str(app_date), str(app_caregiver)))
                    conn.commit()
                    print("Availability canceled!")
                except pymssql.Error:
                    print("Please try again!")
                    cm.close_connection()
                    start()
                    return
                cm.close_connection()
        else:
            print("Please try again!")
            cm.close_connection()
            start()
            return
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    start()






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

    vaccine_name = tokens[1]
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
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        start()
        return

    #if now is patient logging
    if current_patient is not None:
        cm=ConnectionManager()
        conn=cm.create_connection()
        cursor=conn.cursor(as_dict=True)
        show_appoint="select * from Appointments where p_name=%s order by ID asc"
        try:
            cursor.execute(show_appoint,current_patient.username)
            result=cursor.fetchall()
            if len(result) == 0:
                print("Please try again!")
                cm.close_connection()
                start()
                return
            else:
                for row in result:
                    print(row['ID'],row['v_name'],row['Time'],row['c_name'])
        except pymssql.Error:
            print("Please try again!")
            cm.close_connection()
            start()
            return
        cm.close_connection()

    #if now is caregiver logging
    if current_caregiver is not None:
        cm=ConnectionManager()
        conn=cm.create_connection()
        cursor=conn.cursor(as_dict=True)
        c_appoint="select * from Appointments where c_name=%s order by ID asc"
        try:
            cursor.execute(c_appoint,current_caregiver.username)
            c_result=cursor.fetchall()
            if len(c_result) == 0:
                print("Please try again! no appointments")
                cm.close_connection()
                start()
                return
            else:
                for row in c_result:
                    print(row['ID'],row['v_name'],row['Time'],row['p_name'])
        except pymssql.Error:
            print("Please try again!")
            cm.close_connection()
            start()
            return
        cm.close_connection()
    start()

def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    try:
        if current_caregiver is None and current_patient is None:
            print("Please login first")
            return
        else:
            current_patient=None
            current_caregiver=None
            print("Successfully logged out")
            start()
            return
    except pymssql.Error as e:
        print("Logout failed")
        start()
        return
    start()



def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
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
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break


        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
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
