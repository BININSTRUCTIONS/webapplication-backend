from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MessagesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("adminChats", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("adminChats", self.channel_name)

    async def user_started_a_chat(self, message, user=None, email=None):
        print(message)
        print(user)
        print(email)
        await self.send(text_data=json.dumps({"message": "User started a chat"}))

    async def receive(self, text_data):
        data = text_data
        print("Received message: ", data)
        await self.send(text_data=json.dumps({"message": "received your message"}))

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("adminNotificationUpdate", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("adminNotificationUpdate", self.channel_name)

    async def notify(self, information):
        await self.send(text_data=json.dumps(information))
