from database import (
    create_conversation,
    get_conversations,
    get_messages
)


def start_new_chat(user_id):
    """
    Create a new conversation for a user.
    """
    return create_conversation(user_id)


def fetch_conversations(user_id):
    """
    Return all conversations of the logged-in user.
    """
    return get_conversations(user_id)


def fetch_messages(conversation_id):
    """
    Return all messages of a conversation.
    """
    return get_messages(conversation_id)