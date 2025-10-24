import json
from .websocket_connect import WebSocketManager
import logging

logger = logging.getLogger(__name__)

def send_json_message(payload):

    # Send from anywhere
    WebSocketManager.send(payload)            