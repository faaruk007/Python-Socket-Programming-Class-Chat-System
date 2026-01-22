"""
Protocol module for handling JSON message formatting
"""
import json
import config


class Message:
    """Message class for creating and parsing messages"""
    
    @staticmethod
    def create_message(msg_type, sender, receiver=None, text=None, data=None):
        """
        Create a JSON formatted message
        
        Args:
            msg_type: Type of message (from config)
            sender: Sender username
            receiver: Receiver username (optional)
            text: Message text (optional)
            data: Additional data (optional)
        
        Returns:
            JSON string
        """
        message = {
            "type": msg_type,
            "sender": sender,
            "receiver": receiver,
            "text": text,
            "data": data
        }
        return json.dumps(message)
    
    @staticmethod
    def parse_message(json_str):
        """
        Parse JSON message string
        
        Args:
            json_str: JSON formatted string
        
        Returns:
            Dictionary with message data
        """
        try:
            message = json.loads(json_str)

            # DEBUG: Print the parsed message
            print("\n" + "=" * 60)
            print(f"📥 PARSING JSON MESSAGE (Type: {message.get('type')})")
            print("=" * 60)
            print(json.dumps(message, indent=2))
            print("=" * 60 + "\n")


            return json.loads(json_str)

        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def create_connect_message(username):
        """Create connection message"""
        return Message.create_message(config.MSG_CONNECT, username)
    
    @staticmethod
    def create_disconnect_message(username):
        """Create disconnection message"""
        return Message.create_message(config.MSG_DISCONNECT, username)
    
    @staticmethod
    def create_private_message(sender, receiver, text):
        """Create private message"""
        return Message.create_message(config.MSG_PRIVATE, sender, receiver, text)
    
    @staticmethod
    def create_group_message(sender, group_name, text):
        """Create group message"""
        return Message.create_message(config.MSG_GROUP, sender, group_name, text)
    
    @staticmethod
    def create_file_message(sender, receiver, filename, file_data):
        """Create file transfer message"""
        data = {
            "filename": filename,
            "filedata": file_data
        }
        return Message.create_message(config.MSG_FILE, sender, receiver, None, data)
    
    @staticmethod
    def create_error_message(text):
        """Create error message"""
        return Message.create_message(config.MSG_ERROR, "SERVER", None, text)
    
    @staticmethod
    def create_success_message(text):
        """Create success message"""
        return Message.create_message(config.MSG_SUCCESS, "SERVER", None, text)
