from security import get_hashed_id

def user_consent(user_id: str, guild_id: str):
    user_id_hashed = get_hashed_id(user_id)
    guild_id_hashed = get_hashed_id(guild_id)
    # check if is already saved in users (hasedId + hashedGuild)
    # if already saved return False
    # else add to redis queue
    #   return True
    return True

def revoke_user_consent(user_id: str, guild_id: str):
    user_id_hashed = get_hashed_id(user_id)
    guild_id_hashed = get_hashed_id(guild_id)
    # check if is saved in users (hasedId + hashedGuild)
    # if not saved, return False
    # else add to redis queue
    #   return True
    return True

def revoke_user_consent_all(user_id: str):
    user_id_hashed = get_hashed_id(user_id)
    # check if is saved in users (hasedId)
    # if not saved, return False
    # else add to redis queue
    #   return True
    return True


def get_user_redis():
    j = 12
    # gets user from redis if redis user queue is not empty
    # calls get user_data()
    # sends data to postgresql
    # if data is correctly saved in postgre, delete from redis cache