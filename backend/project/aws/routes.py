#pylint: disable = missing-function-docstring ,cyclic-import ,missing-final-newline, missing-module-docstring, missing-function-docstring, line-too-long, too-many-lines, no-name-in-module, import-error, multiple-imports, pointless-string-statement, wrong-import-order

################
#### routes ####
################
from flask import request
from project import mongo, token_required, get_aws_tags
from . import aws_blueprint




@aws_blueprint.route('/api/v1/uploadImage/',  methods=['POST'])
@token_required
def get_aws_tags_for_image():
    # Get fields from request body, check for missing fields

    get_image_data = request.get_json()
    # Check for nulls and whitespaces
    try:
        get_int_user_id = int(get_image_data['user_id'])
    except TypeError:
        return {'error': 'User id must be numeric'}, 403

    try:
        get_image_url = get_image_data['profileImg']
    except TypeError:
        return {'error': 'Please provide image URL'}, 403

    # Get collections
    profile = mongo.db.profile
    aws_tags = mongo.db.aws_tags
    user = mongo.db.user

    try:
        get_profile_id = int(profile.find().skip(
            profile.count_documents({}) - 1)[0]['profile_id'])+1
    except ValueError:
        get_profile_id = 1

    # check if user_id is already in database
    user_id_exists = user.count_documents({'user_id': get_int_user_id})
    if user_id_exists:
        get_tags = get_aws_tags(get_image_url)
        if get_tags['Code'] == 2:
            output = {'Code':2 , 'error':'Invalid Image, Please try another image'}
        else:
            aws_tags.insert_one({
            "profile_id": get_profile_id,
            "user_id": get_int_user_id,
            'AgeRange':get_tags['AgeRange'],
            'Smile':get_tags['Smile'],
            'Eyeglasses':get_tags['Eyeglasses'],
            'Sunglasses':get_tags['Sunglasses'],
            'Gender':get_tags['Gender'],
            'Beard':get_tags['Beard'],
            'Mustache':get_tags['Mustache'],
            'EyesOpen': get_tags['EyesOpen'],
            'MouthOpen': get_tags['MouthOpen'],
            'Emotions': get_tags['Emotions']
        })
            output = {'Code': 1, 'Success':get_tags}

    return output