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


    