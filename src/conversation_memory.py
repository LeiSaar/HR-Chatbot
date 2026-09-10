import json
import os
import redis
from dotenv import load_dotenv

load_dotenv()


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

MAX_MESSAGES = 20

def get_conversation_key(user_id, conversation_id):

    return f"user:{user_id}: conversation:{conversation_id}"


def get_history( user_id, conversation_id):

    key = get_conversation_key(user_id, conversation_id)

    messages = redis_client.lrange(key, 0, -1)

    return [json.loads(message) for message in messages]


def save_message(user_id, conversation_id, role, content):

    key = get_conversation_key(user_id, conversation_id)

    message = {"role": role, "content": content}

    redis_client.rpush(key, json.dumps(message))

    redis_client.ltrim(key,-MAX_MESSAGES, -1)


def clear_conversation(user_id, conversation_id):

    key = get_conversation_key(user_id, conversation_id)

    redis_client.delete(key)


def format_history(user_id, conversation_id):

    history = get_history(user_id, conversation_id)

    if not history:

        return  "No previous conversation found."


    formatted = []


    for message in history:

        role = message["role"]

        content = message["content"]


        if role == "user":

            formatted.append(f"User: {content}")


        elif role == "assistant":

            formatted.append( f"Assistant: {content}")


    return "\n".join(formatted)


# first open the docker desktop app and then run the following command in the terminal:
# docker run -d \--name redis \ -p 6379:6379 \ redis:latest