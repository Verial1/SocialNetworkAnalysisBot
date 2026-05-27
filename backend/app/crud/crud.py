import app.models.models as models

async def insert_messages():
    pass

async def insert_message():
    pass

# DA AGGIUNGERE TRY EXCEPT!!!!!!!!!!!!!!!!!!!!!!!!!!!!
async def get_user_servers(user_id: str, db):
    results = db.query(models.Users.server_id).filter(models.Users.user_id == user_id).all()

    return [r[0] for r in results]

async def get_user_consent(user_id: str, server_id: str, db):
    exists = db.query(models.Users).filter(
        models.Users.user_id == user_id,
        models.Users.server_id == server_id
    ).first() is not None

    return exists

async def remove_consent(user_id: str, server_id: str, db):
    if server_id == "all":
        query = db.query(models.Users).filter(
            models.Users.user_id == user_id
        )       
    else:
        query = db.query(models.Users).filter(
            models.Users.user_id == user_id,
            models.Users.server_id == server_id
        )
        
    if not query.first():
        return "404"
        
    query.delete(synchronize_session=False)

    db.commit()
    return "success"

async def get_user_latest_message(user_id: str, server_id: str, db):
    res = db.query(models.User_Server).filter(
        models.User_Server.user_id == user_id,
        models.User_Server.server_id == server_id
    ).first()

    if not res:
        return "404"

    return res.latest_message_id