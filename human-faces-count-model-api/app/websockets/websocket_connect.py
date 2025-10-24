import json, os, time, ssl, logging, websocket

logger = logging.getLogger(__name__)

WSS_URL = os.getenv("WSS_SERVER")
RETRY_WSS_CONNECT_DELAY = int(os.getenv("RETRY_WSS_CONNECT_DELAY", "5"))

class WebSocketManager:
    ws = None

    @classmethod
    def connect(cls):
        """Connect and retry until success."""
        while True:
            try:
                logger.info("Connecting to WSS server...")
                cls.ws = websocket.create_connection(
                    WSS_URL,
                    sslopt={"cert_reqs": ssl.CERT_NONE},
                )
                logger.info("✅ Connected to WSS server!")
                break
            except Exception as e:
                logger.error("🛑 Connection failed, retrying in %s sec: %s", RETRY_WSS_CONNECT_DELAY, e)
                time.sleep(RETRY_WSS_CONNECT_DELAY)

    @classmethod
    def is_open(cls):
        """Check if connection is active."""
        return cls.ws and cls.ws.sock

    @classmethod
    def send(cls, data):
        """Send JSON data; if closed, reconnect and retry once."""
        if not cls.is_open():
            logger.error("WSS Server not open, reconnecting...")
            cls.connect()

        try:
            cls.ws.send(json.dumps(data))
            logger.info("✅ WSS relay message sent: %s", data)
        except Exception as e:
            logger.error("WSS relay message Send error: %s", e)
            cls.ws = None  # safely mark it dead

    @classmethod
    def listen(cls):
        """Listen for messages and reconnect on disconnect."""
        while True:
            try:
                msg = cls.ws.recv()
                if msg:
                    logger.info("📩 WSS message received: %s", msg)
            except Exception as e:
                logger.warning("🛑 Connection lost, reconnecting...", exc_info=e)
                cls.ws = None
                time.sleep(RETRY_WSS_CONNECT_DELAY)
                cls.connect()
