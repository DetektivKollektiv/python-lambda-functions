from core_layer.db_handler import Session
from uuid import uuid4

def move_mail_addresses_from_submission_to_mail_model():
    with Session() as session:

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