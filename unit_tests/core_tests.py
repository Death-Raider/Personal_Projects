import sys
sys.path.append('core')
from institution_verification import InstitutionVerificationMail
from research_papers import ResearchPapers


print("-"*20 ,"Testing Sending Mail" ,"-"*20)
message = {
    "subject":"Test Mail",
    "body": open("unit_tests/email.html").read()
}
instVerMail = InstitutionVerificationMail(message)
print("Initilized message")
instVerMail.reciever_id = "oragimirox@gmail.com"
print("sending mail to:", instVerMail.reciever_id)
instVerMail.sendMail()

