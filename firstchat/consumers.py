import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .utils import get_create_user, set_offline, get_error_user, all_users_online


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.group_name = 'chat_%s' % 'test_chat'

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        user = await get_create_user(self.username)
        users = await all_users_online()
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'enter_user',
                'username': user.username,
                'online': users,
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await set_offline(self.username)
        users = await all_users_online()
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'leave_user',
                'username': self.username,
                'online': users
            }
        )
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive_json(self, content):
        print(content)
        command = content.get('command')
        if command:
            if command == 'message':
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat_message',
                        'message': content.get('message'),
                        'username': self.username,
                    }
                )
            elif command == 'message_mentions':
                pick_user = await get_error_user(content.get('mentions_user'))
                if pick_user:
                    print(pick_user)
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'chat_message',
                            'message': content.get('message'),
                            'username': self.username,
                        }
                    )
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'mentions_user',
                            'username': self.username,
                            'mentions_user': pick_user.username,
                        }
                    )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'command': 'message',
            'message': event.get('message'),
            'username': event.get('username')
        }))

    async def leave_user(self, event):
        await self.send(text_data=json.dumps({
            'command': 'leave',
            'username': event.get('username'),
            'online': event.get('online'),
        }))

    async def enter_user(self, event):
        await self.send(text_data=json.dumps({
            'command': 'enter',
            'username': event.get('username'),
            'online': event.get('online'),
        }))

    async def mentions_user(self, event):
        if event.get('mentions_user') == self.username:
            await self.send(text_data=json.dumps({
                'command': 'message_mentions',
                'username': event.get('username'),
            }))
