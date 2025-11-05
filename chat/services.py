from django.db.models import Q
from channels.db import database_sync_to_async

from chat.models import Conversation, Message
from users.models import Users


@database_sync_to_async
def get_one_to_one_group(logged_user, user_id):
    """
    Returns a tuple: (unique group name, conversation instance) for a one-to-one chat.
    Creates a Conversation if it doesn't exist.
    Ensures order-independent uniqueness.

    Returns None if the other user does not exist.
    """
    try:
        convo_with = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return None  # indicate user not found

    # Find conversation regardless of user order
    conversation = Conversation.objects.filter(
        Q(user1=logged_user, user2=convo_with) |
        Q(user1=convo_with, user2=logged_user)
    ).first()

    # Create conversation if it doesn't exist
    if not conversation:
        if logged_user.id < convo_with.id:
            conversation = Conversation.objects.create(user1=logged_user, user2=convo_with)
        else:
            conversation = Conversation.objects.create(user1=convo_with, user2=logged_user)

    # Consistent group name
    usernames = sorted([logged_user.username, convo_with.username])
    group_name = f"group_{usernames[0]}_{usernames[1]}"

    return group_name, conversation


@database_sync_to_async
def get_message_history(conversation):
    """
    Returns all messages for the conversation in chronological order as a list of dicts.
    """
    messages = conversation.messages.all().order_by('created_at')
    return [
        {
            'id': str(msg.id),
            'sender': msg.sender.username,
            'receiver': msg.receiver.username,
            'message_text': msg.message_text,
            'message_photo_url': msg.message_photo_url,
            'status': msg.status,
            'timestamp': msg.created_at.isoformat()
        }
        for msg in messages
    ]


@database_sync_to_async
def store_msg(conversation, sender, receiver, message_text, status, message_photo_url=None):
    """
    Creates and stores a new message in the database.
    Returns the message instance.
    """
    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        receiver=receiver,
        message_text=message_text,
        message_photo_url=message_photo_url,
        status=status
    )
    return message,message.sender.username,message.receiver.username



@database_sync_to_async
def verify_sender_receiver(sender_id, receiver_id):
    sender = Users.objects.filter(id=sender_id).first()
    receiver = Users.objects.filter(id=receiver_id).first()
    return sender, receiver


# Example usage in an async consumer or view
# ----------------------------------------------------
# async def my_async_consumer_method(self, logged_user, other_user_id):
#     result = await get_one_to_one_group(logged_user, other_user_id)
#     if result is None:
#         # Handle "user not found"
#         await self.send_json({'error': 'User not found'})
#         return
#
#     group_name, conversation = result
#     messages = await get_message_history(conversation)
#     await self.send_json({'group_name': group_name, 'messages': messages})
