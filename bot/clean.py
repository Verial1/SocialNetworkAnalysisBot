from security import get_hashed_id

def clean_self_server(elem):
    return {
        "server_id": str(elem.get("id"))
    }

def clean_message(elem):
    msg = elem[0]

    return {
        "message_id": get_hashed_id(str(msg.get("id"))),
        "content": msg.get("content", ""),
        "author_id": get_hashed_id(str(msg.get("author", {}).get("id"))),
        "channel_id": get_hashed_id(str(msg.get("channel_id"))),
        "timestamp": msg.get("timestamp"),
        "mention_everyone": msg.get("mention_everyone"),
        "mentions": [get_hashed_id(str(u.get("id"))) for u in msg.get("mentions", [])],
        "mention_roles": [str(r) for r in msg.get("mention_roles", [])],
        "attachments": [
            {
                "index": i, 
                "type": a.get("content_type", "unknown")
            } for i, a in enumerate(msg.get("attachments", []))
        ],
        "embeds": [
            {
                "type": e.get("type"),
                "url": e.get("url"),
                "title": e.get("title"),
                "description": e.get("description"),
                "author": e.get("author", {}).get("name"),
                "thumbnail_url": e.get("thumbnail", {}).get("url")
            } for e in msg.get("embeds", [])
        ],
        "responds_to": get_hashed_id(str(msg.get("message_reference", {}).get("message_id"))) 
                       if msg.get("message_reference") else None
    }

def clean_user(elem):
    server_picture = elem.get("avatar")
    if server_picture == None:
        server_picture = elem.get("user", {}).get("avatar")

    return{
        "server_username": elem.get("nick"),
        "server_picture": server_picture
    }

def clean_guild(elem):
    return{
        "name": elem.get("name"),
        "picture": elem.get("icon"),
    }