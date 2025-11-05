import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection
from channels.db import database_sync_to_async
import uuid
import datetime

class ChatCustomer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get login user info
        self.user = self.scope['user']
        # Get user_id which is received through params
        self.user_id = self.scope['url_route']['kwargs']['user_id']

        # Verify if there is connection between sender and receiver and if no connection then create connection
        from chat.services import get_one_to_one_group
        self.group_name , self.conversation = await get_one_to_one_group(self.user,self.user_id)

        # Prevent chatting with yourself
        if str(self.user.id) == str(self.user_id):
            # Close the connection immediately
            await self.close(code=4001)  # Custom close code (optional)
            return

        # Add this channel to the group
        await self.channel_layer.group_add(
            self.group_name,  
            self.channel_name  
        )
        
        await self.accept()

        # Store the onlione_users in redis
        r = get_redis_connection("default")
        r.sadd("online_users",str(self.user.id))

        await self.send(text_data=json.dumps({
            'message': 'Connected to WebSocket'
        }))

    async def disconnect(self, close_code):
        # Remove the user from redis when disconnected to indicate user is offline
        r= get_redis_connection("default")
        r.srem("online_users",str(self.user.id))

        # Remove the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        # Extract the msg received from frontend
        data = json.loads(text_data)
        message = data.get('message', '')
        message_photo_url = data.get('message_photo_url','')

        # Dummy id to match 2 msg send ir pending and send or selivered msg was same
        dummy_id = str(uuid.uuid4())

        # Checking wheather the receiver is online or not if online msg status will be delivered
        # Check with the help of redis as online user is stored in redis
        user_online_info = await user_online(str(self.user.id))
        if user_online_info == 1:   # ✅ use == instead of is
            status = "delivered"
        else:
            status = "sent"

        # verify the sender and receiver 
        from chat.services import verify_sender_receiver,store_msg
        sender,receiver = await verify_sender_receiver(self.user.id,self.user_id)
        
        # Send the message to the group befored storing in db for indicating msg was pending
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',  # triggers chat_message method
                'message': message,
                "sender" : sender.username,
                "receiver" : receiver.username,
                "status" : "pending",
                "message_photo_url" : message_photo_url,
                "timestamp":datetime.datetime.now().isoformat(),
                "match_id" : dummy_id,
                "id" : None
            }
        )

        # Call the function to store the msg and receive the sender and receiver username because object should not be send directly in response
        store_message,sender_username, receiver_username = await store_msg(conversation=self.conversation,sender=sender,receiver=receiver,message_text=message,status=status)

        # Again send the message to indicate msg is delivered or sent
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',  # triggers chat_message method
                'message': store_message.message_text,
                "sender" : sender_username,
                "receiver" : receiver_username,
                "status" : store_message.status,
                "timestamp" : store_message.created_at.isoformat(),
                "id" : str(store_message.id),
                "message_photo_url" : store_message.message_photo_url,
                "match_id" : dummy_id
            }
        )

    # This method is called for all messages sent to the group
    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': str(event['sender']),
            'receiver': str(event['receiver']),
            'status': event['status'],
            'id': event['id'],
            'message_photo_url': event['message_photo_url'],
            'timestamp': event['timestamp'],
            "match_id" : event['match_id'],
        }))


@database_sync_to_async
def user_online(user_id):
    # Check where user exist or not in redis
    r = get_redis_connection("default")
    is_online = r.sismember("online_users", user_id)
    return is_online # 1 if exist and 0 if doesnot exist

