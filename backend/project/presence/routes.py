# pylint: disable = line-too-long, inconsistent-return-statements, unused-variable, broad-except, trailing-whitespace, cyclic-import,bare-except, missing-module-docstring, missing-function-docstring, too-many-lines, no-name-in-module, import-error, multiple-imports, pointless-string-statement, too-many-locals, wrong-import-order, anomalous-backslash-in-string
from datetime import datetime
from flask import request
from project import mongo, token_required, get_batch_count
from pymongo.collection import ReturnDocument
from . import presence_blueprint
ACTION = "$elemMatch"
AMERICANINDIAN = "American Indian"
ASIANAMERICAN= "Asian"
AFROAMERICAN = "Black or African American"
HISPLATINO = "Hispanic or Latino"
PACIFICISLANDER = "Pacific Islander"
WHITEAMERICAN = "White"
OTHER = "Other"
UNDISCLOSED = "Prefer Not To Say"
ERROR = "No reviews found"


################
#### routes ####
################

# ALL FUTURE DATA VALIDATION



@presence_blueprint.route('/api/v1/addPresence/', methods=['POST'])
@token_required
def add_presence_to_pool():
    date_joined = datetime.utcnow()
    profile_data = request.get_json()
    presence = mongo.db.presence
    user_presence_count = presence.count_documents(
        {"$and": [{"user_id": profile_data['user_id']}, {"profile_id": profile_data['profile_id']}]})
    if user_presence_count == 0:
        output = insert_data(profile_data)
        if output != "ERROR":
            result = {
                "profile_id": profile_data['profile_id'],
                "state": profile_data['state'],
                "zip": profile_data['zip'],
                "city": profile_data['city'],
                "email": profile_data['email'],
                "position": profile_data['position'],
                "aboutMe":  profile_data['aboutMe'],
                "education": profile_data['education'],
                "experience": profile_data['experience'],
                "user_id": profile_data['user_id'],
                "profileName": profile_data['profileName'],
                "profileImg": profile_data['profileImg'],
                "first_name": profile_data['first_name'],
                "last_name": profile_data['last_name'],
                "added_on": date_joined,
                "reviewed_by": output['reviewed_by'],
                "gender": profile_data['gender'],
                "ethnicity":profile_data['ethnicity']
            }
        else:
            result = {'code': 4, "error": "User account does not exist"}, 403
    else:
        result = {'code': 4, "error": "User presence already exists"}, 403

    return result


def insert_data(profile_information):
    date_joined = datetime.utcnow()
    presence = mongo.db.presence
    print("Print Gender", profile_information['gender'])
    create_presence = presence.insert_one({
        "profile_id": profile_information['profile_id'],
        "state": profile_information['state'],
        "zip": profile_information['zip'],
        "city": profile_information['city'],
        "email": profile_information['email'],
        "user_id": profile_information['user_id'],
        "profileName": profile_information['profileName'],
        "profileImg": profile_information['profileImg'],
        "first_name": profile_information['first_name'],
        "last_name": profile_information['last_name'],
        "position": profile_information['position'],
        "aboutMe":  profile_information['aboutMe'],
        "education": profile_information['education'],
        "experience": profile_information['experience'],
        "added_on": date_joined,
        "reviewed_by": [],
        "gender": profile_information['gender'],
        "ethnicity":profile_information['ethnicity']
    })
    if create_presence:
        return profile_information
    return "ERROR"


@presence_blueprint.route('/api/v1/getAllPresence/<reviewer_id>/', methods=['GET'])
@token_required
def get_all_presence_for_reviewer(reviewer_id):
    if request.method == 'GET':
        try:
            reviewer_id = int(reviewer_id)
        except TypeError:
            return {'error': 'reviewer id must be numeric'}, 403
        presences = mongo.db.presence
        output = []
        try:
            for presence in presences.find({"reviewed_by": {"$not": {'$elemMatch': {"reviewer_id": reviewer_id}}}}).limit(int(get_batch_count())):
                output.append({
                    'user_id': int(presence['user_id']),
                    'profile_id': presence['profile_id'],
                    'profile_name': presence['profileName'],
                    'profileImg': presence['profileImg'],
                    'gender': presence['gender'],
                    'state': presence['state'],
                    'zip': presence['zip'],
                    'city': presence['city'],
                    'email': presence['email'],
                    'first_name': presence['first_name'],
                    'last_name': presence['last_name'],
                    'aboutMe': presence['aboutMe'],
                    'position': presence['position'],
                    'education': presence['education'],
                    'experience': presence['experience'],
                    'reviewed_by': presence['reviewed_by']
                })
            if len(output) > 0:
                return {'count': len(output), 'results': output}
            return {'code': 4, 'error': "No more presence to be reviewed"}
        except Exception as error:
            print("Exception ", error)
            return {'code': 4, 'error': "No presence found"}, 403

# Checks for existence of a particular batch
def batch_existence(reviewer_id):
    # Get collections
    batch_details_col = mongo.db.batch_details
    # Check if a batch exists which can accept more entries based on batch size
    get_details = batch_details_col.find_one({'$and': [
    {
      'hr_user_id': int(reviewer_id)
    },
    {
      'can_accept_more': int(1)
    }]})
    return get_details

# Fetch all details of one particular user
def get_user_details(user_id):
    # Get collections
    user_details_col = mongo.db.user
    # Check if a batch exists which can accept more entries based on batch size
    send_user_details = user_details_col.find_one({"user_id": user_id})

    return send_user_details

@presence_blueprint.route('/api/v1/savePresenceReview/', methods=['PATCH'])
@token_required
def update_presence_with_review():
    date_joined = datetime.utcnow()
    reviewer = request.get_json()
    presence_profile_id = int(reviewer['profile_id'])
    presence_user_id = int(reviewer['user_id'])

    try:
        feedback = reviewer['feedback']
        reviewer_id = int(feedback['reviewer_id'])
        application_status = feedback['application_status']
    except TypeError:
        return {'error': 'feedback details cannot be empty'}, 403


    query = {"$and": [{"user_id": presence_user_id},
                      {"profile_id": presence_profile_id}]}

    query_2 = {'$and': [
    {
      'hr_user_id': int(reviewer_id)
    },
    {
      'can_accept_more': int(1)
    }]}

    options = {"upsert": False}


    # Get collections
    presence_col = mongo.db.presence
    batch_details_col = mongo.db.batch_details


    try:
        get_acceptance_status = batch_existence(reviewer_id)
        if get_acceptance_status is None:
            use_same_batch = False
        else:
            use_same_batch = True
    except ValueError:
        use_same_batch = False

    try:
        if presence_col.count_documents(query) == 1:
            user = get_user_details(presence_user_id)
            profile_details = presence_col.find_one_and_update(
                    query, {"$push": {'reviewed_by': feedback}}, return_document=ReturnDocument.AFTER)
            result = {
                    "profile_id": profile_details['profile_id'],
                    "state": profile_details['state'],
                    "zip": profile_details['zip'],
                    "city": profile_details['city'],
                    "email": profile_details['email'],
                    "position": profile_details['position'],
                    "gender": profile_details['gender'],
                    "aboutMe":  profile_details['aboutMe'],
                    "education": profile_details['education'],
                    "experience": profile_details['experience'],
                    "user_id": profile_details['user_id'],
                    "profileName": profile_details['profileName'],
                    "profileImg": profile_details['profileImg'],
                    "first_name": profile_details['first_name'],
                    "last_name": profile_details['last_name'],
                    "added_on": date_joined,
                    "reviewed_by": profile_details['reviewed_by']
                }
            if use_same_batch is False:
                set_batch_details = batch_details_col.insert_one({
                    "hr_user_id": reviewer_id,
                    "batch_no": 1,
                    "batch_size": int(get_batch_count()),
                    "can_accept_more": 1,
                    "reviewed_count":1,
                    "reviewed_by": [{
                        "profile_id": presence_profile_id,
                        "user_id": presence_user_id,
                        "gender":user['gender'],
                        "ethnicity":user['ethnicity'],
                        "date_of_birth":user['date_of_birth'],
                        "reviewer_id": reviewer_id,
                        "application_status": application_status
                                }]
                })
            elif use_same_batch:
                get_one_batch = batch_existence(reviewer_id)
                get_batch_size = int(get_one_batch['batch_size'])
                get_reviewed_count = int(get_one_batch['reviewed_count'])
                reviewed_by_data = {
                                "profile_id": presence_profile_id,
                                "user_id": presence_user_id,
                                "gender":user['gender'],
                                "ethnicity":user['ethnicity'],
                                "date_of_birth":user['date_of_birth'],
                                "reviewer_id": reviewer_id,
                                "application_status": application_status
                                }
                if get_reviewed_count < get_batch_size:

                    update = {
                                "$set": {"reviewed_count":int(get_reviewed_count + 1)},
                                "$push": {"reviewed_by": reviewed_by_data}
                            }

                    update_batch_details = batch_details_col.find_one_and_update(query_2, update, options)
                else:
                    update_status = {
                                "$set": {"can_accept_more": 0}
                            }

                    update_acceptance_status = batch_details_col.find_one_and_update(query_2, update_status, options)
                    increment_batch_no = int(get_one_batch['batch_no'] + 1)
                    create_batch_details = batch_details_col.insert_one({
                                        "hr_user_id": reviewer_id,
                                        "batch_no": increment_batch_no,
                                        "batch_size": int(get_batch_count()),
                                        "can_accept_more": 1,
                                        "reviewed_count":1,
                                        "reviewed_by": [{
                                            "profile_id": presence_profile_id,
                                            "user_id": presence_user_id,
                                            "gender":user['gender'],
                                            "ethnicity":user['ethnicity'],
                                            "date_of_birth":user['date_of_birth'],
                                            "reviewer_id": reviewer_id,
                                            "application_status": application_status
                                                    }]
                })
            else:
                return {'code': 1, 'error': 'Unable to update batch details, Please delete duplicate instance of batch details'}, 403
        else:
            result = {'code': 2, 'error': "User presence not found"}, 200
    except Exception as error:
        print("Exception", error)
        result = {'code': 3, 'error': str(error)}, 403
    return result


@presence_blueprint.route('/api/v1/getCount/<reviewer_id>/', methods=['GET'])
@token_required
def get_presence_count(reviewer_id):
    try:
        reviewer_id = int(reviewer_id)
    except TypeError:
        return {'error': 'reviewer id must be numeric'}, 403



    declined_male_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"gender": "Male"}]}
    declined_female_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"gender": "Female"}]}
    declined_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"gender": "Other"}]}
    declined_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"gender": "Prefer Not To Say"}]}
    accepted_male_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"gender": "Male"}]}
    accepted_female_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"gender": "Female"}]}
    accepted_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"gender": "Other"}]}
    accepted_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"gender": "Prefer Not To Say"}]}


    declined_male_count = mongo.db.presence.count_documents(
        declined_male_query)
    declined_female_count = mongo.db.presence.count_documents(
        declined_female_query)
    declined_other_count = mongo.db.presence.count_documents(
        declined_other_query)
    declined_undisclosed_count = mongo.db.presence.count_documents(
        declined_undisclosed_query)
    accepted_male_count = mongo.db.presence.count_documents(
        accepted_male_query)
    accepted_female_count = mongo.db.presence.count_documents(
        accepted_female_query)
    accepted_other_count = mongo.db.presence.count_documents(
        accepted_other_query)
    accepted_undisclosed_count = mongo.db.presence.count_documents(
        accepted_undisclosed_query)

    try:
        result = {
            "reviewer_id": reviewer_id,
            "declined_male_count": declined_male_count,
            "declined_female_count": declined_female_count,
            "declined_other_count": declined_other_count,
            "declined_undisclosed_count": declined_undisclosed_count,
            "accepted_male_count": accepted_male_count,
            "accepted_female_count": accepted_female_count,
            "accepted_other_count": accepted_other_count,
            "accepted_undisclosed_count" : accepted_undisclosed_count
        }
    except Exception as error:
        print("Exception", error)
        result = {'code': 4, 'error': ERROR}, 403
    return result

@presence_blueprint.route('/api/v1/getCount/<reviewer_id>/<batch_no>/', methods=['GET'])
# @token_required
def get_batch_presence_count(reviewer_id, batch_no):
    try:
        reviewer_id = int(reviewer_id)
        batch_no = int(batch_no)
    except TypeError:
        return {'error': 'reviewer id and batch no must be numeric'}, 403


    declined_male_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "gender": "Male"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_female_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined" , "gender": "Female"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined" , "gender": "Other"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined" , "gender": "Prefer Not To Say"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_male_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted" , "gender": "Male"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_female_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted" , "gender": "Female"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted" , "gender": "Other"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted" , "gender": "Prefer Not To Say"}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}



    declined_male_count = mongo.db.batch_details.count_documents(
        declined_male_query)
    declined_female_count = mongo.db.batch_details.count_documents(
        declined_female_query)
    declined_other_count = mongo.db.batch_details.count_documents(
        declined_other_query)
    declined_undisclosed_count = mongo.db.batch_details.count_documents(
        declined_undisclosed_query)
    accepted_male_count = mongo.db.batch_details.count_documents(
        accepted_male_query)
    accepted_female_count = mongo.db.batch_details.count_documents(
        accepted_female_query)
    accepted_other_count = mongo.db.batch_details.count_documents(
        accepted_other_query)
    accepted_undisclosed_count = mongo.db.batch_details.count_documents(
        accepted_undisclosed_query)

    try:
        result = {
            "reviewer_id": reviewer_id,
            "declined_male_count": declined_male_count,
            "declined_female_count": declined_female_count,
            "declined_other_count": declined_other_count,
            "declined_undisclosed_count": declined_undisclosed_count,
            "accepted_male_count": accepted_male_count,
            "accepted_female_count": accepted_female_count,
            "accepted_other_count": accepted_other_count,
            "accepted_undisclosed_count" : accepted_undisclosed_count
        }
    except Exception as error:
        print("Exception", error)
        result = {'code': 4, 'error': ERROR}, 403
    return result


@presence_blueprint.route('/api/v1/getAcceptanceRate/<user_id>/', methods=['GET'])
@token_required
def get_acceptance_rate_for_jobseeker(user_id):
    try:
        user_id = int(user_id)
    except TypeError:
        return {'error': 'reviewer id must be numeric'}, 403

    submitted_presences = list(
        mongo.db.presence.find({"user_id": user_id}))

    result = {}

    for presence in submitted_presences:
        profile_name = presence["profileName"]
        reviewer_response = presence["reviewed_by"]

        print(profile_name)

        accepted_count = 0
        declined_count = 0

        for response in reviewer_response:
            status = response["application_status"]
            if status == "Accepted":
                accepted_count += 1
            elif status == "Declined":
                declined_count += 1

        temp = {}
        temp["accepted"] = accepted_count
        temp["declined"] = declined_count

        result[profile_name] = temp

    return result

@presence_blueprint.route('/api/v1/getCount/Ethnicity/<reviewer_id>/<batch_no>/', methods=['GET'])
# @token_required
def get_batch_presence_by_ethnicity_count(reviewer_id, batch_no):
    try:
        reviewer_id = int(reviewer_id)
        batch_no = int(batch_no)
    except TypeError:
        return {'error': 'reviewer id and batch no must be numeric'}, 403


    declined_american_indian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": AMERICANINDIAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_asian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": ASIANAMERICAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_black_american_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": AFROAMERICAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_hispanic_latino__query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": HISPLATINO}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_pacific_islander_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": PACIFICISLANDER}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_white_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": WHITEAMERICAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": OTHER}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    declined_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined", "ethnicity": UNDISCLOSED}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}

    accepted_american_indian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": AMERICANINDIAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_asian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": ASIANAMERICAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_black_american_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": AFROAMERICAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_hispanic_latino_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": HISPLATINO}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_pacific_islander_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": PACIFICISLANDER}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_white_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": WHITEAMERICAN}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": OTHER}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}
    accepted_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted", "ethnicity": UNDISCLOSED}}}, {"batch_no": batch_no}, {"hr_user_id": reviewer_id}]}


    declined_american_indian_count = mongo.db.presence.count_documents(
        declined_american_indian_query)
    declined_asian_count = mongo.db.presence.count_documents(
        declined_asian_query)
    declined_black_american_count = mongo.db.presence.count_documents(
        declined_black_american_query)
    declined_hispanic_latino_count = mongo.db.presence.count_documents(
        declined_hispanic_latino__query)
    declined_pacific_islander_count = mongo.db.presence.count_documents(
        declined_pacific_islander_query)
    declined_white_count = mongo.db.presence.count_documents(
        declined_white_query)
    declined_other_count = mongo.db.presence.count_documents(
        declined_other_query)
    declined_undisclosed_count = mongo.db.presence.count_documents(
        declined_undisclosed_query)


    accepted_american_indian_count = mongo.db.presence.count_documents(
        accepted_american_indian_query)
    accepted_asian_count = mongo.db.presence.count_documents(
        accepted_asian_query)
    accepted_black_american_count = mongo.db.presence.count_documents(
        accepted_black_american_query)
    accepted_hispanic_latino_count = mongo.db.presence.count_documents(
        accepted_hispanic_latino_query)
    accepted_pacific_islander_count = mongo.db.presence.count_documents(
        accepted_pacific_islander_query)
    accepted_white_count = mongo.db.presence.count_documents(
        accepted_white_query)
    accepted_other_count = mongo.db.presence.count_documents(
        accepted_other_query)
    accepted_undisclosed_count = mongo.db.presence.count_documents(
        accepted_undisclosed_query)


    try:
        result = {
            "reviewer_id": reviewer_id,
            "declined_american_indian_count": declined_american_indian_count,
            "declined_asian_count": declined_asian_count,
            "declined_black_american_count": declined_black_american_count,
            "declined_hispanic_latino_count": declined_hispanic_latino_count,
            "declined_pacific_islander_count": declined_pacific_islander_count,
            "declined_white_count": declined_white_count,
            "declined_other_count": declined_other_count,
            "declined_undisclosed_count": declined_undisclosed_count,

            "accepted_american_indian_count": accepted_american_indian_count,
            "accepted_asian_count": accepted_asian_count,
            "accepted_black_american_count": accepted_black_american_count,
            "accepted_hispanic_latino_count": accepted_hispanic_latino_count,
            "accepted_pacific_islander_count" : accepted_pacific_islander_count,
            "accepted_white_count": accepted_white_count,
            "accepted_other_count": accepted_other_count,
            "accepted_undisclosed_count": accepted_undisclosed_count
        }
    except Exception as error:
        print("Exception", error)
        result = {'code': 4, 'error': ERROR}, 403
    return result


@presence_blueprint.route('/api/v1/getCountByEthnicity/<reviewer_id>/', methods=['GET'])
@token_required
def get_presence_count_by_ethnicity(reviewer_id):
    try:
        reviewer_id = int(reviewer_id)
    except TypeError:
        return {'error': 'reviewer id must be numeric'}, 403


    declined_american_indian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": AMERICANINDIAN}]}
    declined_asian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": ASIANAMERICAN}]}
    declined_black_american_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": AFROAMERICAN}]}
    declined_hispanic_latino__query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": HISPLATINO}]}
    declined_pacific_islander_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": PACIFICISLANDER}]}
    declined_white_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": WHITEAMERICAN}]}
    declined_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": OTHER}]}
    declined_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Declined"}}}, {"ethnicity": UNDISCLOSED}]}

    accepted_american_indian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": AMERICANINDIAN}]}
    accepted_asian_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": ASIANAMERICAN}]}
    accepted_black_american_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": AFROAMERICAN}]}
    accepted_hispanic_latino_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": HISPLATINO}]}
    accepted_pacific_islander_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": PACIFICISLANDER}]}
    accepted_white_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": WHITEAMERICAN}]}
    accepted_other_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": OTHER}]}
    accepted_undisclosed_query = {"$and": [{"reviewed_by": {ACTION: {
        "reviewer_id": reviewer_id, "application_status": "Accepted"}}}, {"ethnicity": UNDISCLOSED}]}


    declined_american_indian_count = mongo.db.presence.count_documents(
        declined_american_indian_query)
    declined_asian_count = mongo.db.presence.count_documents(
        declined_asian_query)
    declined_black_american_count = mongo.db.presence.count_documents(
        declined_black_american_query)
    declined_hispanic_latino_count = mongo.db.presence.count_documents(
        declined_hispanic_latino__query)
    declined_pacific_islander_count = mongo.db.presence.count_documents(
        declined_pacific_islander_query)
    declined_white_count = mongo.db.presence.count_documents(
        declined_white_query)
    declined_other_count = mongo.db.presence.count_documents(
        declined_other_query)
    declined_undisclosed_count = mongo.db.presence.count_documents(
        declined_undisclosed_query)


    accepted_american_indian_count = mongo.db.presence.count_documents(
        accepted_american_indian_query)
    accepted_asian_count = mongo.db.presence.count_documents(
        accepted_asian_query)
    accepted_black_american_count = mongo.db.presence.count_documents(
        accepted_black_american_query)
    accepted_hispanic_latino_count = mongo.db.presence.count_documents(
        accepted_hispanic_latino_query)
    accepted_pacific_islander_count = mongo.db.presence.count_documents(
        accepted_pacific_islander_query)
    accepted_white_count = mongo.db.presence.count_documents(
        accepted_white_query)
    accepted_other_count = mongo.db.presence.count_documents(
        accepted_other_query)
    accepted_undisclosed_count = mongo.db.presence.count_documents(
        accepted_undisclosed_query)


    try:
        result = {
            "reviewer_id": reviewer_id,
            "declined_american_indian_count": declined_american_indian_count,
            "declined_asian_count": declined_asian_count,
            "declined_black_american_count": declined_black_american_count,
            "declined_hispanic_latino_count": declined_hispanic_latino_count,
            "declined_pacific_islander_count": declined_pacific_islander_count,
            "declined_white_count": declined_white_count,
            "declined_other_count": declined_other_count,
            "declined_undisclosed_count": declined_undisclosed_count,

            "accepted_american_indian_count": accepted_american_indian_count,
            "accepted_asian_count": accepted_asian_count,
            "accepted_black_american_count": accepted_black_american_count,
            "accepted_hispanic_latino_count": accepted_hispanic_latino_count,
            "accepted_pacific_islander_count" : accepted_pacific_islander_count,
            "accepted_white_count": accepted_white_count,
            "accepted_other_count": accepted_other_count,
            "accepted_undisclosed_count": accepted_undisclosed_count
        }
    except Exception as error:
        print("Exception", error)
        result = {'code': 4, 'error': ERROR}, 403
    return result
