
# Created by: Aaron Rose, Security Architect @ Check Point Software Technologies
# Version 1.0
# This script is provided "as is" and without warranty of any kind, you are solely responsible for any compromise or loss of data that may result from using this Script.
# This script is designed to run directly on the Check Point Management Server.  If you wish to run this from an alternate location, you will need the mgmt_cli binary and must adapt the code to use the mgmt server as the target to login/make changes/publish/logout
from os import path
import os
import getpass
import json

# define date variables
# note: you must capitalize the first letter of the month.  If the script does not match, use gui dbedit.exe to find database value of users expiration date, the capitalization of the month is most likely the issue
oldExpiration = "31-Jul-2020"
newExpiration = "31-Jul-2021"
#
# function for login to mgmt api and retrieve sid


def apiLogin(logincommand):
    stream = os.popen(logincommand)
    loginOutput = stream.read()
    jsonLoginOutput = json.loads(loginOutput)
    return jsonLoginOutput["sid"]


# function to publish changes using sid from login
def apiPublish(sid):
    stream = os.popen("mgmt_cli publish --session-id " + sid)
    publishOutput = stream.read()
    print (publishOutput)

# function to logout after publish using sid from login


def apiLogout(sid):
    stream = os.popen("mgmt_cli logout --session-id " + sid)
    logoutOutput = stream.read()
    print (logoutOutput)

# function to logout after publish using sid from login


def retrieveUsers(sid):
    stream = os.popen(
        "mgmt_cli -f json show generic-objects class-name com.checkpoint.objects.classes.dummy.CpmiUser details-level full --session-id " + sid)
    usersOutput = stream.read()
    jsonUsersOutput = json.loads(usersOutput)
    return jsonUsersOutput["objects"]


def filterByExpiration(users, oldExpiration):
    return [u for u in users if u["adminExpirationBaseData"]["expirationDate"] == oldExpiration]


def updateUsers(filteredUsers, sid, newExpiration):
    for user in filteredUsers:
        updateUserCommand = 'mgmt_cli -f json set generic-object uid "{}" .adminExpirationBaseData.expirationDate "{}" --session-id {}'.format(
            user["uid"], newExpiration, sid)
        print (updateUserCommand)
        os.popen(updateUserCommand)


# prompt user for login credentials to mgmt api server, then build the login command as a variable to pass to login function
username = raw_input("API Username:")
password = getpass.getpass("Password for " + username + ":")
logincommand = "mgmt_cli login user " + username + \
    " password " + password + " --format json"

sid = apiLogin(logincommand)
users = retrieveUsers(sid)
filteredUsers = filterByExpiration(users, oldExpiration)
print "-----"
print filteredUsers
print "-----"
updateUsers(filteredUsers, sid, newExpiration)
apiPublish(sid)
apiLogout(sid)
