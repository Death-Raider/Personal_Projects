import yagmail
import json

class InstitutionVerificationMail:
    def __init__(self,message):
        self.message = message
        self.institution_lookup = json.load(open("./data/institutions.json"))
        self.gamil_id = "wish.gsolve@gmail.com"
        self.gamil_password = "." # if mail as 2FA then get the "App password" in the 2FA settings.

    def takeInput(self):
        self.institution = str(input("Enter Institution Name:").rstrip())
        self.location = str(input("Enter Institution Location:").rstrip())

    def getInstitutionId(self):
        self.reciever_id = self.institution_lookup[self.institution][self.location] # get the mail id for the institution

    def sendMail(self):
        print("logging in")
        yag = yagmail.SMTP(self.gamil_id, self.gamil_password)
        print("logged in successfully")
        print("sending mail")
        yag.send(to = self.reciever_id, subject = self.message["subject"], contents = [self.message["body"]])
        print("mail sent")
        print("logging out")
        yag.close()
        print("logged out")
        