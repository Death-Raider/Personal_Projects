"""
- Uses core files to create higher level functions for processing which include:
* Obtaining information using OCR and update user profile
* Giving proper inputs for research papers and maintaining fixed results 
* Filter chats for explict content and words

- Handles the database queries which include:
* storing and retreving user profile details in the format (./data/user_data_template.json)
* store and retreving text message for chatrooms
"""

#connect to database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
from models import Post, User

cred = credentials.Certificate('')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

def create_user(user: User, uid: str, email: str, password: str):
    try:
        userCreated = auth.create_user(
            uid=uid,
            email=email,
            password=password
        )

        data = {
            "name": user.name,
            "pfp": user.pfp,
            "description": user.description,
            "USER_TYPE": user.USER_TYPE,
            "verification": user.verification,
            "gender": user.gender,
            "age": user.age,
            "researcher": user.researcher
        }

        db.collection('customUsersCollection').document(uid).set(data)
        return userCreated
    except Exception as e:
        return str(e)

def get_user(mail: str):
    try:
        user = auth.get_user_by_email(mail)
        user_data_collection = db.collection('customUsersCollection')
        user_data= user_data_collection.document(user.uid).get().to_dict()
        if user_data != None:
            data = {
                "name": user_data["name"],
                "pfp": user_data["pfp"],
                "description": user_data["description"],
                "USER_TYPE": user_data["USER_TYPE"],
                "verification": user_data["verification"],
                "age": user_data["age"],
                "gender": user_data["gender"],
                "researcher": user_data["researcher"]
            }

            return data
    except Exception as e:
        return str(e)
    
def create_post(post: Post):
    try:
        db = firestore.client()
        doc_ref = db.collection('posts').document()
        doc_ref.set(post.model_dump())
        return doc_ref.id
    except Exception as e:
        return str(e)
    
