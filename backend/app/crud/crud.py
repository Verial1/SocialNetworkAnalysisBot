import app.models.models as models

# DA USARE SQLALCHEMY ASYNC (ATTUALMENTE STO USANDO LA VERSIONE SYNC)

async def insert_messages():
    pass

async def insert_message():
    pass

async def get_user_servers(user_id: str, db):
    results = db.query(models.Users.server_id).filter(models.Users.user_id == user_id).all()
    return [r[0] for r in results]

async def get_user_consent(user_id: str, server_id: str, db):
    return db.query(models.Users).filter(
        models.Users.user_id == user_id,
        models.Users.server_id == server_id
    ).first() 

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
        return False
        
    query.delete(synchronize_session=False)

    return "success"

async def get_user_latest_message(user_id: str, server_id: str, db):
    res = db.query(models.User_Server).filter(
        models.User_Server.user_id == user_id,
        models.User_Server.server_id == server_id
    ).first()

    if not res:
        return None

    return res.latest_message_id