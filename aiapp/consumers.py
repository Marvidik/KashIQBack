from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .service import get_ai_response


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser
        self.user = await self.get_user_from_token()
        
        if self.user is None or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)  # Custom close code for unauthorized
        else:
            await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        question = data.get('question')

        if not question:
            await self.send(text_data=json.dumps({"error": "Question is required"}))
            return

        # Run AI response safely in thread pool
        response = await database_sync_to_async(get_ai_response)(self.user, question)

        await self.send(text_data=json.dumps({"answer": response}))

    @database_sync_to_async
    def get_user_from_token(self):
        from rest_framework.authtoken.models import Token
        query_string = self.scope.get("query_string", b"").decode()
        params = dict(q.split("=") for q in query_string.split("&") if "=" in q)
        token = params.get("token")

        if token:
            try:
                token_obj = Token.objects.get(key=token)
                return token_obj.user
            except Token.DoesNotExist:
                return None
        return None
