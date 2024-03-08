class ClientRequest:
    @staticmethod
    def hello():
        return "HELLO_FROM\n"
    
    @staticmethod
    def list():
        return "LIST\n"
    
    @staticmethod
    def send():
        return "SEND\n"
    
    
class ServerResponses:
    @staticmethod
    def badRequestBody():
        return "BAD_RQST_BODY\n"
    
    @staticmethod
    def badRequestHeader():
        return "BAD_RQST_HEADER\n"

    @staticmethod
    def busy():
        return "TOO_MANY_USERS\n"
    
    @staticmethod
    def inUse():
        return "IN_USE\n"
    
    @staticmethod
    def okList():
        return "LIST_RECEIVED\n"
    
    @staticmethod
    def okSend():
        return "SENT\n"
    
    @staticmethod
    def delivery():
        return "DELIVERY\n"

    @staticmethod
    def noUserInDb():
        return "NO_USER\n"

    @staticmethod 
    def hello():
        return "HELLO\n"

    @staticmethod
    def unknown():
        return "UNKNOWN\n"


class ClientResponses:
    @staticmethod
    def loggedIn():
        return "You logged in"
    @staticmethod
    def msgSent():
        return "Message sent!"
    
    @staticmethod
    def thanks():
        return "Thank you for using our program! See you again."


class Error:
    @staticmethod
    def serverIsFull():
        return "Servers is full!"
    
    @staticmethod
    def usernameExists():
        return "User with such nickname already exists!"

    @staticmethod 
    def errorStartingTasks(e):
        print(f"Error starting tasks: {e}")
    
    @staticmethod
    def invalidOrUnvalidUser():
        return "Invalid or unavailable user"

    @staticmethod
    def wrongCommand():
        return "Wrong command! Please try again."
    