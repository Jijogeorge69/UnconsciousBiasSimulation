#pylint: disable = line-too-long, cyclic-import,relative-beyond-top-level, trailing-newlines,inconsistent-return-statements, trailing-whitespace, bare-except, missing-module-docstring, missing-function-docstring, too-many-lines, no-name-in-module, import-error, multiple-imports, pointless-string-statement, wrong-import-order, anomalous-backslash-in-string
from datetime import datetime
import bcrypt
from flask_jwt_extended import create_access_token
from flask import request
from project import mongo
from pymongo import ReturnDocument
from . import user_blueprint


# Registration API
@user_blueprint.route('/api/v1/createUser/', methods=['POST'])
def create_user():
    # Get fields from request body, check for missing fields
    try:
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        hashed_password = bcrypt.hashpw(request.get_json()['password'].encode('utf-8'), bcrypt.gensalt())
        registration_type = request.get_json()['registration_type']
        gender = request.get_json()['gender']
        date_of_birth = request.get_json()['date_of_birth']
    except:
        return {'code': 4, 'error': 'Missing request body'}, 403
    # Check for blanks
    if first_name == '' or last_name == '' or request.get_json()['password'] == '' or email == '' or registration_type == '':
        return {'code': 4, 'error': "Field/s cannot be blank"}, 403
    # Get collections
    users = mongo.db.user
    # Get last user_id and increment it by one, When no records found set user_id=1
    try:
        user_id = int(users.find().skip(users.count_documents({}) - 1)[0]['user_id']) + 1
    except:
        user_id = 1

    date_joined = datetime.utcnow()

    # Check if email is already in database
    email_exists = users.count_documents({'email': email})

    output = {}
    # when email id exists in DB throw below error message
    if email_exists:
        output = {'code': 4, 'error': "Email is already in use"}, 403
    else:
        user = users.insert_one({
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password' : hashed_password,
            'date_joined' : date_joined,
            'registration_type' : registration_type,
            'gender': gender,
            'date_of_birth': date_of_birth,
            'contact_details' : request.get_json()['contact_details'],
        })
        # Upon successful insert create JWT access token, update token in authtoken collection
        if user:
            access_token = create_access_token(identity={'user_id': user_id, 'date_joined': date_joined})
            tokens = mongo.db.authtoken
            tokens.insert_one({"user_id": user_id, "key": access_token, 'created': datetime.utcnow()})
            output = {'token': access_token, 'user': {'user_id': user_id, 'first_name': first_name, 'email': email, 'registration_type': registration_type}}

    return output

# Login API
@user_blueprint.route('/api/v1/login/', methods=['POST'])
def user_login():
    # Get fields from request body, check for missing fields
    try:
        email = request.get_json()['email']
        password = request.get_json()['password']
    except:
        return {'code': 4, 'error': 'Missing request body'}, 403
    # Check for blanks
    if request.get_json()['password'] == '' or email == '':
        return {'code': 4, 'error': "Field/s cannot be blank"}, 403
    # Get collections
    users = mongo.db.user
    user = users.find_one({"email" : email})

    if not user:
        return {'code': 4, 'error':"User not found"}, 403
    # Check if password matches
    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        access_token = create_access_token(identity={'id': int(user['user_id']), 'date_joined': user['date_joined']})

        tokens = mongo.db.authtoken
         # Create token and update token into authtoken collection, this is to maintain session considering future logout scenario
        tokens.find_one_and_update({"user_id": int(user['user_id'])}, {"$set": {"key": access_token, 'created': datetime.utcnow()}}, upsert=True)
        user = users.find_one_and_update({"user_id": int(user['user_id'])}, {"$set": {'last_login': datetime.utcnow()}}, return_document=ReturnDocument.AFTER)
        output = {"user_id" : user['user_id'], "email" : user['email'], "token": access_token, "registration_type" : user['registration_type'], "first_name" : user['first_name'], "last_name":user['last_name'], "gender": user['gender'], "date_of_birth": user['date_of_birth']}

    else:
        return {'code': 4, "error": "Invalid password"},403

    return output

### LOGOUT
@user_blueprint.route('/api/v1/logout/', methods=['POST'])
### In future when session managment is implemented, UI should send the same token to logout API, Verify whether the token sent matches the one in DB
def logout():
    # Initialize variables to be inserted and displayed
    try:
        user_id = request.get_json()['user_id']
    except:
        return {"error": "Missing user_id"}, 403

    # Convert id to integer
    try:
        user_id = int(user_id)
    except:
        return {"error": "user_id must be numerical"}, 403

    # Get collections
    users = mongo.db.users_customuser

    # Check if user exists in users collection
    users = mongo.db.user
    user = users.find_one({"user_id" : user_id})

    if user:
        # Check if user exists in tokens collection
        tokens = mongo.db.authtoken
        db_token = tokens.find_one({'user_id': user_id})
        if not db_token:
            output = {'code': 4, "error": "User_id does not have existing token"}, 403
            return output
        tokens.find_one_and_delete({'user_id': user_id})
        output = {"success": "Successfully logged out"}
    else:
        output = {'code': 4, "error": "User_id does not exist"}, 403
    return output

### GET ALL USERS
@user_blueprint.route('/api/v1/users/', methods=['GET'])
# @token_required
def get_all_users():
    if request.method == 'GET':
        users = mongo.db.user

        output = []
        try:
            for user in users.find():

                output.append({
                    'user_id': int(user['user_id']),
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'date_joined': user['date_joined'],
                    'registration_type': user['registration_type'],
                    'gender': user['gender'],
                    'date_of_birth':user['date_of_birth'],
                    'contact_details': user['contact_details']
                    })

            return {'count': len(output), 'results': output}
        except:
            return {'code': 4, 'error':"No users found"}, 403


### GET, EDIT, DELETE USER
@user_blueprint.route('/api/v1/users/<user_id>/', methods=['GET', 'PATCH', 'DELETE'])

def edit_one_user(user_id):

    # Convert id to integer
    try:
        user_id = int(user_id)
    except:
        return {'code': 5, 'error':"id must be numerical"}, 403

    # Get request
    if request.method == 'GET':
        user = mongo.db.user.find_one({'user_id': user_id})

    # Delete request
    elif request.method == 'DELETE':
        user = mongo.db.user.find_one_and_delete({'user_id': user_id})
        countprofile = mongo.db.profile.count_documents({'user_id': user_id})


        # Equivalent of cascaded delete in MongoDB. When user is deleted. Delete his/her profiles and tokens.
        mongo.db.profile.delete_many({'user_id': user_id})
        mongo.db.authtoken.delete_many({'user_id': user_id})
        try:
            output = {
                    'user_id': int(user['user_id']),
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'date_joined': user['date_joined'],
                    'registration_type': user['registration_type'],
                    'gender': user['gender'],
                    'date_of_birth':user['date_of_birth'],
                    'contact_details': user['contact_details'],
                    'count_of_profiles_deleted': countprofile


            }
        except:
            output = {'code': 5, "error": "User does not exist"}, 403
        return output
    # Patch Request
    elif request.method == 'PATCH':
        fields = ['first_name', 'last_name', 'registration_type','gender','date_of_birth', 'contact_details']
        pairs = {}
        request_body = request.get_json()

        # Check for fields that need to be updated
        for field in request_body:
            if field in fields:
                pairs[field] = request_body[field]

        # Update user information
        mongo.db.user.find_one_and_update(
            {"user_id": user_id}, {"$set": pairs})
        user = mongo.db.user.find_one({"user_id": user_id})

    try:
        output = {
                    'user_id': int(user['user_id']),
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'date_joined': user['date_joined'],
                    'registration_type': user['registration_type'],
                    'gender': user['gender'],
                    'date_of_birth':user['date_of_birth'],
                    'contact_details': user['contact_details']
                  }
    except:
        output = {'code': 5, "error": "User does not exist"}, 403
    return output
