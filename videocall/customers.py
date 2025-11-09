# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class WebRTCConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_name = None  # Will store username after registration
#         await self.accept()

#     async def disconnect(self, close_code):
#         if self.user_name:
#             # Remove user from group when they disconnect
#             await self.channel_layer.group_discard(
#                 f"user_{self.user_name}",
#                 self.channel_name
#             )

#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         # Handle registration
#         if data.get("type") == "register":
#             self.user_name = data["name"]
#             await self.channel_layer.group_add(
#                 f"user_{self.user_name}",
#                 self.channel_name
#             )
#             return

#         # Send signaling messages to the target user only
#         target = data.get("target")
#         if target:
#             await self.channel_layer.group_send(
#                 f"user_{target}",
#                 {
#                     "type": "signal_message",
#                     "message": data
#                 }
#             )

#     async def signal_message(self, event):
#         # Forward the message to the WebSocket
#         await self.send(text_data=json.dumps(event["message"]))

# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class WebRTCConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope['user']
#         self.user_id = self.scope['url_route']['kwargs']['user_id']

#         # Prevent self-chat
#         if str(self.user.id) == str(self.user_id):
#             await self.close(code=4001)
#             return

#         # Get the one-to-one chat group
#         from chat.services import get_one_to_one_group
#         self.group_name, self.conversation = await get_one_to_one_group(self.user, self.user_id)

#         # Add channel to group
#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()
#         print(f"WebSocket connected for user {self.user.id} in group {self.group_name}")

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)
#         print(f"WebSocket disconnected for user {self.user.id}")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         target = data.get("target")

#         # Forward signaling message only if target exists
#         if target:
#             from chat.services import get_one_to_one_group
#             target_group_name, _ = await get_one_to_one_group(self.user, target)
#             await self.channel_layer.group_send(
#                 target_group_name,
#                 {
#                     "type": "signal_message",
#                     "message": data
#                 }
#             )

#     async def signal_message(self, event):
#         await self.send(text_data=json.dumps(event["message"]))

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from chat.customers import user_online

class WebRTCustomer(AsyncWebsocketConsumer):
    async def connect(self):
        self.logged_user = self.scope["user"]
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']

        # Prevent self calling
        if str(self.logged_user.id) == str(self.receiver_id):
            await self.close(code=40001)
            return
        
        from chat.services import get_one_to_one_group
        self.group_name, _ = await get_one_to_one_group(self.logged_user,self.receiver_id)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Check if receiver is online
        is_online = await user_online(str(self.receiver_id))

        if not is_online:
            # Notify caller and close connection
            await self.send(text_data=json.dumps({
                "type": "receiver_status",
                "message": "Receiver is offline",
                "receiver_id": self.receiver_id
            }))
            await self.close(code=40002)  # Custom code for offline receiver
            return

        # Accept connection only if receiver is online
        await self.accept()




    async def disconnect(self, close_code):
        from chat.services import get_one_to_one_group
        self.group_name, _ = await get_one_to_one_group(self.logged_user, self.receiver_id)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = str(self.logged_user.id)
        target = data.get("target")

        if target:
            # Add sender info
            data["sender"] = sender_id

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "signal_message",
                    "message": data
                }
            )

    async def signal_message(self, event):
        message = event["message"]
        sender_id = message.get("sender")

        # Don't send the message back to the sender
        if str(self.logged_user.id) == str(sender_id):
            return

        await self.send(text_data=json.dumps(message))

