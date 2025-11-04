import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatCustomer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the group name from the URL
        self.group_name = self.scope['url_route']['kwargs']['group_name']

        # Add this channel to the group
        await self.channel_layer.group_add(
            self.group_name,  
            self.channel_name  
        )
        
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Connected to WebSocket'
        }))

    async def disconnect(self, close_code):
        # Remove from the group when disconnected
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print("Disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        # Send the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',  # triggers chat_message method
                'message': message
            }
        )

    # This method is called for all messages sent to the group
    async def chat_message(self, event):
        message = event['message']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
