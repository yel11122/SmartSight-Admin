# admin_panel/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

# This consumer will handle all connections to the 'ws/status/' path.
class StatusConsumer(AsyncWebsocketConsumer):
    # The groups list is used by the Channel Layer to send messages to all connected users.
    # We define a single, constant group name for all admin status updates.
    notification_group_name = 'admin_notifications'

    # --- Connection and Disconnection Handlers ---

    async def connect(self):
        # 1. Join the designated group
        # This adds the current WebSocket connection's channel name to the group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        # 2. Accept the connection (This is mandatory)
        await self.accept()
        print(f"[{self.scope['user']}]: WebSocket CONNECTED to group '{self.notification_group_name}'")


    async def disconnect(self, close_code):
        # Leave the designated group on disconnect
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
        print(f"[{self.scope['user']}]: WebSocket DISCONNECTED (Code: {close_code})")

    
    # --- Message Receiver (not used yet, but good practice to include) ---

    # This method is called when the client sends a message to the server
    async def receive(self, text_data=None, bytes_data=None):
        # Since this consumer is only for server-to-client notifications, 
        # we don't expect to receive messages from the client, but we can log it.
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            print(f"[{self.scope['user']}]: Received message: {message}")

    # --- Message Sender (Custom method for handling group messages) ---
    
    # This is the handler for messages sent to the group via the Channel Layer.
    # The 'type' must match the function name (e.g., 'status_update' calls status_update)
    async def status_update(self, event):
        # Pull the payload from the event dictionary
        text_data = event['text']

        # Send the received data back to the WebSocket client
        await self.send(text_data=json.dumps(text_data))
        print(f"[{self.scope['user']}]: Sent group message: {text_data}")
#STOP