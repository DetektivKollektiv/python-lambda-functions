import boto3
from core_layer.db_handler import Session
from core_layer.handler.mail_handler import create_mail
from core_layer.model.mail_model import Mail
from core_layer.model.user_model import User
from uuid import uuid4
import os


def get_all_users_from_cognito():

    """
    cognitos list_users() returns a maximum of 60 users:
    https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_ListUsers.html#CognitoUserPools-ListUsers-request-Limit
    this function retruns a list of all users
    """

    try:
        stage = os.environ['STAGE']
    except:
        stage = 'dev'

    if stage == 'prod':
        userpoolid = 'eu-central-1_xARdELzvv'
    elif stage == 'qa':
        userpoolid = 'eu-central-1_Uk1f9Sydt'
    else:
        userpoolid = 'eu-central-1_edLkAIQVL'

    cognito = boto3.client('cognito-idp', region_name = 'eu-central-1')
    
    users = []
    next_page = None
    kwargs = {
        'UserPoolId': userpoolid
    }

    users_remain = True
    while(users_remain):
        if next_page:
            kwargs['PaginationToken'] = next_page
        response = cognito.list_users(**kwargs)
        users.extend(response['Users'])
        next_page = response.get('PaginationToken', None)
        users_remain = next_page is not None

    return users


def move_mail_addresses_from_submission_to_mail_model():
    with Session() as session:

        # Move mail addresses from submission_model to mail_model
        result = session.execute('SELECT * FROM submissions')
        for row in result:
            if row.status == 'confirmed':
                if len(session.execute(f"SELECT * FROM mails WHERE email = '{row.mail}'").fetchall()) == 0:
                    session.execute(f"""INSERT INTO mails(id, email, status)
                                    VALUES ('{str(uuid4())}', '{row.mail}', '{row.status}');
                                    """)
                    session.commit()
                    
                    mail_id = session.execute(f"""SELECT * FROM mails WHERE email = '{row.mail}'""").first().id
                    session.execute(f"""UPDATE submissions
                                    SET mail_id = '{mail_id}'
                                    WHERE mail = '{row.mail}';
                                    """)   
                    session.commit()


        # Add mail addresses from cognito to mail_model
        cognito_user_list = get_all_users_from_cognito()
        
        for cognito_user in cognito_user_list:
            user_id_from_cognito = cognito_user['Attributes'][0]['Value']
            user_mail_from_cognito = cognito_user['Attributes'][2]['Value']

            mail_from_db = session.query(Mail).filter(Mail.email == user_mail_from_cognito).first()
            user_from_db = session.query(User).filter(User.id == user_id_from_cognito).first()

            if mail_from_db is None and user_from_db is not None: # create mail_model entry if not yet exists and link it to existing user
                mail = Mail(email = user_mail_from_cognito, status = 'confirmed')
                create_mail(mail, session)
                user_from_db.mail_id = mail.id
                session.commit()
            elif mail_from_db is not None and user_from_db is not None: # link user to existing mail_model entry
                list_of_user_ids_connected_to_mail_from_db = [x.id for x in mail_from_db.users]
                if user_id_from_cognito not in list_of_user_ids_connected_to_mail_from_db and user_from_db.id == user_id_from_cognito:
                    user_from_db.mail_id = mail_from_db.id
                    session.commit()