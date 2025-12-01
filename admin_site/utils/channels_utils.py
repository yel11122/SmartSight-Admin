import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_admin_status_update(update_type, data):
    """
    Broadcasts a structured real-time update to all clients in the 'admin_status' group.

    This function should be called from synchronous Django code (like views or signals).
    It uses async_to_sync to safely interact with the asynchronous channel layer.
    """
    
    # Get the channel layer instance (using the in-memory backend defined in settings)
    channel_layer = get_channel_layer()
    
    # Structure the message payload
    message_payload = {
        # 'type' maps directly to the method name in consumers.py (status_update -> status.update)
        'type': 'status.update', 
        'status_data': { # Send all your data inside the 'status_data' key
            'update_type': update_type,
            'payload': data
        }
    }

    try:
        # Use async_to_sync to call the asynchronous group_send function
        async_to_sync(channel_layer.group_send)(
            "admin_status",  # The group name the consumer joined
            message_payload
        )
        # print(f"Successfully broadcasted {update_type} to admin_status group.")
    except Exception as e:
        # In case the channel layer configuration is bad, print the error
        print(f"ERROR: Failed to send channel message: {e}")
