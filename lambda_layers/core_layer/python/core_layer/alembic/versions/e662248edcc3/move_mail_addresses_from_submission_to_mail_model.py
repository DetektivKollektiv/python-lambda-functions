import boto3
from core_layer.db_handler import Session
from core_layer.handler.mail_handler import create_mail
from core_layer.model.mail_model import Mail
from core_layer.model.user_model import User
from uuid import uuid4
import os

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

        client = boto3.client('cognito-idp', region_name = 'eu-central-1')
        user_list = client.list_users(UserPoolId = userpoolid)['Users']
        for cognito_user in user_list:
            user_id_from_cognito = cognito_user['Attributes'][0]['Value']
            user_mail_from_cognito = cognito_user['Attributes'][2]['Value']

            mail_from_db = session.query(Mail).filter(Mail.email == user_mail_from_cognito).first()
            user_from_db = session.query(User).filter(User.id == user_id_from_cognito).first()

            if mail_from_db is None and user_from_db is not None: # create entry if not yet exists
                mail = Mail(email = user_mail_from_cognito, status = 'confirmed', user_id = user_id_from_cognito)
                create_mail(mail, session)
            elif hasattr(mail_from_db, 'user_id') and user_from_db is not None: # link user to existing mail_model entry
                if mail_from_db.user_id is None:
                    if user_from_db.id == user_id_from_cognito:
                        mail_from_db.user_id = user_id_from_cognito
                        session.add(mail_from_db)
                        session.commit()