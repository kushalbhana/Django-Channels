from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
import asyncio
from time import sleep
from asgiref.sync import async_to_sync
import json
from .models import Chat, Group
from channels.db import database_sync_to_async


class MySyncConsumer(SyncConsumer):
    def websocket_connect(self, event):
        # print('Websocket connected...', event)
        # print('Channel Layer...', self.channel_layer) #get default channel layer from the project
        # print('Channel Name...', self.channel_name) #get default channel name from the project
        # print("Group Name....", self.scope['url_route']['kwargs']['groupname'])
        self.group_name= self.scope['url_route']['kwargs']['groupname']
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.send({
            'type': 'websocket.accept'
        })

    def websocket_receive(self, event):
        # print("Message Recieved from client", event['text']) 
        # print("Type of Message Recieved from client", type(event['text'])) 
        try:
            data= json.loads(event['text'])
            group=  Group.objects.get(name= self.group_name)

            if self.scope['user'].is_authenticated:
                # print(self.scope['user'])
                # Create new chat Object
                chat= Chat(
                    content= data['msg'],
                    group= group
                    )
                chat.save()
                data['user'] = self.scope['user'].username

                async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    'type': 'chat.message',
                    'message': json.dumps(data)

                })
            else:
                self.send({
                    'type': 'websocket.send',
                    'text': json.dumps({'msg': 'Login required'})

                })
        except:
            pass

    def chat_message(self, event):
        # print('Event...', event)
        self.send({
            'type': 'websocket.send',
            'text': event['message']
        })
 

    def websocket_disconnect(self, event):
        # print("Websocket Disconnected", event)
        # print('Channel Layer...', self.channel_layer) #get default channel layer from the project
        # print('Channel Name...', self.channel_name) #get default channel name from the project
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
             self.channel_name
             )
        raise StopConsumer


class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('Websocket connected...', event)
        print('Channel Layer...', self.channel_layer) #get default channel layer from the project
        print('Channel Name...', self.channel_name) #get default channel name from the project
        self.group_name= self.scope['url_route']['kwargs']['groupname']
        self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            'programmers',
            self.channel_name
        )

        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print("Message Recieved from client", event['text']) 
        print("Type of Message Recieved from client", type(event['text'])) 
        try:
            data= json.loads(event['text'])
            group= await database_sync_to_async(Group.objects.get)(name= self.group_name)

        # Create new chat Object
            chat= Chat(
                content= data['msg'],
                group= group
                )
            await database_sync_to_async(chat.save)()
        except:
            pass

        await self.channel_layer.group_send(
            'programmers',
            {
                'type': 'chat.message',
                'message': event['text']
            }
        )

    async def chat_message(self, event):
        print('Event...', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['message']
        })
 

    async def websocket_disconnect(self, event):
        print("Websocket Disconnected", event)
        print('Channel Layer...', self.channel_layer) #get default channel layer from the project
        print('Channel Name...', self.channel_name) #get default channel name from the project
        await self.channel_layer.group_discard(
            'programmers',
             self.channel_name
             )
        raise StopConsumer
    