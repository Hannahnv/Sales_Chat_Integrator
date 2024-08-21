import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Chat
from django.contrib.auth.models import User
import logging
from .tasks import process_chat_message
from channels.exceptions import StopConsumer

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat_room'
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()

    async def receive(self, text_data):
        try:
            logger.info(f'Received message: {text_data}')
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']

            await self.save_message(username, message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )
            
            task = process_chat_message.delay(message, username)  # Pass both arguments
            result = await sync_to_async(task.get)(timeout=10)  # Set a timeout
            
            response_message = result or "Đã xử lý yêu cầu của bạn."
                
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': response_message,
                    'username': 'System',
                }
            )
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'An error occurred while processing your message.'
            }))

    async def chat_message(self, event):
        logger.info(f'Sending message: {event}')
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, username, message):
        user = User.objects.get(username=username)
        Chat.objects.create(user=user, message=message)
