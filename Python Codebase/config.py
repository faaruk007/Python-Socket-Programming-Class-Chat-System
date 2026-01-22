"""
Configuration settings for ClassChat Project
"""

# Server Configuration
SERVER_HOST = '127.0.0.1'  # localhost
SERVER_PORT = 5555
BUFFER_SIZE = 131072  # Change to 128 KB

# Message Types
MSG_CONNECT = "CONNECT"
MSG_DISCONNECT = "DISCONNECT"
MSG_PRIVATE = "PRIVATE"
MSG_GROUP = "GROUP"
MSG_FILE = "FILE"
MSG_CREATE_GROUP = "CREATE_GROUP"
MSG_JOIN_GROUP = "JOIN_GROUP"
MSG_LIST_USERS = "LIST_USERS"
MSG_LIST_GROUPS = "LIST_GROUPS"
MSG_ERROR = "ERROR"
MSG_SUCCESS = "SUCCESS"
MSG_OFFLINE = "OFFLINE"
MSG_ACK = "ACK"  # Acknowledgement messages
MSG_REGISTER_USER = "REGISTER_USER"  # User registration
MSG_USER_STATUS = "USER_STATUS"  # Check if user exists
MSG_HISTORY_REQUEST = "HISTORY_REQUEST"  # NEW: Request conversation history
MSG_HISTORY_RESPONSE = "HISTORY_RESPONSE"  # NEW: Send conversation history
MSG_KEY_EXCHANGE = "KEY_EXCHANGE"  # Encryption key exchange



# File Transfer
MAX_FILE_SIZE = 10 * 1024 * 1024
CHUNK_SIZE = 4096


# Encryption
USE_ENCRYPTION = True


# Database
DB_FILE = 'classchat.db'


# I/O Multiplexing Options
IO_METHOD = 'select'  # Options: 'select', 'poll', 'epoll'

# Message History
HISTORY_MESSAGE_LIMIT = 20  # Number of previous messages to load

