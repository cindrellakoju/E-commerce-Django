from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.http import JsonResponse

class WebRTCustomer(AsyncWebsocketConsumer):
    async def connect(self):
        self.logged_user = self.scope["user"]
        self.receiver_id = self.scope['query_string'].decode().split("=")[-1]

        # Prevent self-calling
        if str(self.logged_user.id) == str(self.receiver_id):
            await self.close(code=40001)
            return
        
        from users.services import verify_user
        if self.receiver_id:
            user = await verify_user(user_id=self.receiver_id)
            if isinstance(user, JsonResponse):
                await self.close(code=40002)
                return
        self.username = self.logged_user.username
            
        from chat.services import get_one_to_one_group
        self.group_name, _ = await get_one_to_one_group(
            self.logged_user, self.receiver_id
        )

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print(f"{self.username} connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'signal_message',
                'message': data,
                'sender': self.username
            }
        )

    async def signal_message(self, event):
        if event['sender'] != self.username:
            await self.send(text_data=json.dumps(event['message']))
