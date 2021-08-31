################################################################################
#
#   File Name: Developer Challenge - Cameron Graham.py
#   File Type: Python File (.py)
#   Author:    Cameron Graham
#   Date:      26 August 2021
#   Description: Developer Challenge for Time-Lapse-Systems    
#                - Allow user to enter integers (any value/amount)
#                - Sort integers entered by the user, user chooses direction
#                - Store sorted sequence in a database (SQLite)
#                - Feedback results to user
#                - Display results of all sorts (inc direction & time taken)
#                - Allow user to export all sorts as JSON
#
################################################################################
import sqlite3
import time
import json

# sqliteSetup()
# Creates a database & table (if not already in existance),
# then creates a connection and cursor.
# 
# Returns 
#   connection - A connection to the SQLite Database
#   cursor - Object used to interact with records.
def sqliteSetup():
    connection = sqlite3.connect("sortDatabase.db")
    cursor = connection.cursor()
    # Checking if a table named SORTS already exists in sortDatabase.db
    tables = cursor.execute("""SELECT Name FROM sqlite_master WHERE type='table' AND Name='SORTS'; """).fetchall()
    # Creates SORTS table if it doesn't exist.
    if tables == []:
        cursor.execute("CREATE TABLE SORTS (Numbers TEXT, Direction TEXT, TimeTaken TEXT)")
    return connection, cursor

connection, cursor = sqliteSetup()

# print_menu()
# 
# Function to output a menu to the console.
def print_menu():
    print("\n")
    print(15 * "-" , "MENU" , 15 * "-")
    print("1. Sort new integer list")
    print("2. Display all previous sorts")
    print("3. Export all previous sorts as JSON")
    print("4. Exit")
    print(36 * "-")

# inputIntegers()
#  
# Function to allow the user to input a list of integers
#
# Returns
#   integerList - The integers entered by the user, stored as an array
#   (-1 is returned if the user makes an error)
def inputIntegers():
    try:
        userInput = input("Enter a list of integers, separated with a space. (E.g. 17 42 7 22 5)\n").strip() # Strip removes leading/trailing spaces to prevent errors.
        integerList = userInput.split(" ")
        for i in range(0, len(integerList)):
            integerList[i] = int(integerList[i])
        return integerList
    except:
        if userInput != "":
            print("Input Failed - Input contained a non-integer character")
        else:
            print("Input Failed - Input was empty")
        return -1

# sortNumbers(integers, direction)
#
# Parameters
#   integers - Array containing integers entered by the user
#   direction - Boolean (True - Descending, False - Ascending)
# 
# Returns
#   integers - Sorted list of integers
#   endTime - time when sort is complete (in nanoseconds)
def sortNumbers(integers, direction):
    integers.sort(reverse=direction)
    endTime = time.perf_counter_ns()
    return integers, endTime

# getSorts()
# 
# Gets all of the sorts from the SQLite database
#
# Returns
#   rows - Array of rows from the database
#   (-1 is returned if no rows are found)
def getSorts():
    rows = cursor.execute("SELECT * FROM SORTS").fetchall()
    if rows != []:
        return rows
    else:
        return -1

# Main program loop
# 
# Controls option selection from menu
# and calls other logic functions
while True:
    print_menu()
    menuSelection = input("Select an option: ")
    # Sort new integer list
    if menuSelection == '1':
        integers = inputIntegers()
        # inputIntegers() returns -1 if user makes an error,
        # this if statement checks for -1 and skips to the
        # next iteration of the main loop, without doing
        # any processing to the integers.
        if integers == -1:
            continue
        # Asks the user for a direction to sort the integers,
        # repeats the question until a valid input is given.
        while True:
            sortDirection = input("Sort Direction:\n1. Ascending\n2. Descending\n")
            startTime = time.perf_counter_ns()
            if sortDirection == '1':
                integers, endTime = sortNumbers(integers, False)
                sortType = "Ascending"
                break
            elif sortDirection == '2':
                integers, endTime = sortNumbers(integers, True)
                sortType = "Descending"
                break
            else:
                print("Invalid sort direction selection.")
        # Converts the integer array into a string, with the
        # numbers seperated by commas
        integersString = ",".join([str(i) for i in integers])

        # Attempts to insert the sorted integers, sort direction and time taken
        # into the database, error is handled in case of failure.
        try:
            cursor.execute("INSERT INTO SORTS VALUES ('"+ integersString + "', '"+ sortType +"', '"+ str(endTime-startTime) +"')")
            if cursor.rowcount >= 1:
                print("\n" + integersString +": Succesfully inserted into database. Process took "+ str(endTime-startTime) +"ns")
            connection.commit()
        except:
            print("INSERT query failed.")
    # Display all previous sorts    
    elif menuSelection == '2':
        rows = getSorts()
        # getSorts() returns -1 if user makes an error,
        # this if statement checks for -1 and skips to the
        # next iteration of the main loop, without doing
        # any processing to the integers.
        if rows == -1:
            print("No sorts stored in database")
            continue
        print("Numbers | Direction | Time Taken (ns)")
        for row in rows:
            print(row[0] + " | " + row[1] + " | " + row[2])

    # Export all previous sorts as JSON
    elif menuSelection == '3':
        rows = getSorts()
        # getSorts() returns -1 if user makes an error,
        # this if statement checks for -1 and skips to the
        # next iteration of the main loop, without doing
        # any processing to the integers.
        if rows == -1:
            print("No sorts stored in database")
            continue
        jsonArray = []
        for row in rows:
            jsonArray.append({"Integers":row[0], "Direction":row[1], "Time":row[2]})
        jsonString = json.dumps(jsonArray)
        jsonFile = open("sorts.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        print("Sorts exported to sorts.json")
    
    # Exit Program
    elif menuSelection == '4':
        print("Exiting program.")
        break
    
    # Invalid selection check.
    else:
        print("Invalid selection")

#Close connection once program is finished.
connection.close()