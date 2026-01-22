"""
ClassChat Server - WITH ENCRYPTION
Multi-threaded server with message history, conversation threading and RSA+AES encryption
"""
import socket
import threading
import json
from datetime import datetime
import config
from protocol import Message
from database import MessageDatabase
from encryption import MessageEncryption
import traceback
import time


class ClassChatServer:
    """Multi-threaded chat server with conversation history"""
    
    def __init__(self, host=config.SERVER_HOST, port=config.SERVER_PORT):
        """Initialize server"""
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.client_threads = {}
        self.groups = {}
        self.lock = threading.Lock()
        self.database = MessageDatabase()
        self.running = False
        
        # ENCRYPTION SUPPORT
        self.server_encryption = MessageEncryption()
        self.client_encryptors = {}  # Store encryption handler for each client
        
        # Generate RSA key pair for the server
        if config.USE_ENCRYPTION:
            print("[SERVER] Generating RSA key pair...")
            self.server_encryption.generate_rsa_keys()
            print("[SERVER] RSA keys generated successfully")
            print("[SERVER] 🔒 Encryption ENABLED")
    
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"[SERVER] ClassChat Server started on {self.host}:{self.port}")
            print(f"[SERVER] Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"[SERVER] New connection from {address}")
                    
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,)
                    )
                    thread.daemon = True
                    thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"[SERVER ERROR] Accept error: {e}")
                    
        except Exception as e:
            print(f"[SERVER ERROR] Failed to start server: {e}")
            traceback.print_exc()
    
    def handle_client(self, client_socket):
        """Handle individual client connection"""
        username = None
        try:
            username = self.handle_connect(client_socket)
            
            if username:
                while self.running:
                    try:
                        data = client_socket.recv(config.BUFFER_SIZE)
                        if not data:
                            break
                        
                        message_str = data.decode('utf-8')
                        
                        # DECRYPT MESSAGE if encryption is enabled
                        if config.USE_ENCRYPTION and username in self.client_encryptors:
                            try:
                                # Decrypt the message using client's session key
                                message_str = self.client_encryptors[username].decrypt_message(message_str)
                            except Exception as e:
                                print(f"[SERVER ERROR] Decryption error for '{username}': {e}")
                                continue
                        
                        message = Message.parse_message(message_str)
                        
                        if message:
                            msg_type = message.get('type')
                            
                            if msg_type == config.MSG_PRIVATE:
                                self.handle_private_message(message)
                            elif msg_type == config.MSG_GROUP:
                                self.handle_group_message(message)
                            elif msg_type == config.MSG_FILE:
                                self.handle_file_transfer(message)
                            elif msg_type == config.MSG_CREATE_GROUP:
                                self.handle_create_group(message)
                            elif msg_type == config.MSG_JOIN_GROUP:
                                self.handle_join_group(message)
                            elif msg_type == config.MSG_LIST_USERS:
                                self.handle_list_users(username)
                            elif msg_type == config.MSG_LIST_GROUPS:
                                self.handle_list_groups(username)
                            elif msg_type == config.MSG_HISTORY_REQUEST:
                                self.handle_history_request(message)
                            elif msg_type == config.MSG_DISCONNECT:
                                break
                                
                    except Exception as e:
                        print(f"[SERVER ERROR] Error handling message from {username}: {e}")
                        break
                        
        except Exception as e:
            print(f"[SERVER ERROR] Client handler error: {e}")
            traceback.print_exc()
        finally:
            if username:
                self.handle_disconnect(username)
            try:
                client_socket.close()
            except:
                pass
    
    def handle_connect(self, client_socket):
        """Handle client connection with encryption key exchange: Very Important Part"""
        try:
            data = client_socket.recv(config.BUFFER_SIZE)
            if not data:
                return None
            
            message_str = data.decode('utf-8')
            message = Message.parse_message(message_str)
            
            if message and message.get('type') == config.MSG_CONNECT:
                username = message.get('sender')
                
                with self.lock:
                    if username in self.clients:
                        error_msg = Message.create_error_message(
                            f"Username '{username}' is already taken"
                        )
                        client_socket.send(error_msg.encode())
                        return None
                    
                    self.clients[username] = client_socket
                    print(f"[SERVER] '{username}' connected")
                    
                    # REGISTER USER IN DATABASE
                    self.database.register_user(username)
                    print(f"[SERVER] User '{username}' registered in database")
                    
                    success_msg = Message.create_success_message(
                        f"Welcome to ClassChat, {username}!"
                    )
                    client_socket.send(success_msg.encode())
                    
                    # ENCRYPTION KEY EXCHANGE
                    if config.USE_ENCRYPTION:
                        print(f"[SERVER] Starting key exchange with '{username}'")
                        
                        # Send RSA public key to client
                        public_key_pem = self.server_encryption.get_public_key_pem()
                        key_exchange_msg = Message.create_message(
                            config.MSG_KEY_EXCHANGE,
                            "SERVER",
                            username,
                            None,
                            {"public_key": public_key_pem, "step": "server_public_key"}
                        )
                        client_socket.send(key_exchange_msg.encode())
                        print(f"[SERVER] Sent RSA public key to '{username}'")
                        
                        # Wait for encrypted session key from client
                        key_data = client_socket.recv(config.BUFFER_SIZE)
                        if not key_data:
                            print(f"[SERVER ERROR] Failed to receive session key from '{username}'")
                            return None
                        
                        key_message_str = key_data.decode('utf-8')
                        key_message = Message.parse_message(key_message_str)
                        
                        if key_message and key_message.get('type') == config.MSG_KEY_EXCHANGE:
                            encrypted_session_key = key_message.get('data', {}).get('encrypted_session_key')
                            
                            if encrypted_session_key:
                                # Create encryption handler for this client
                                client_encryptor = MessageEncryption()
                                client_encryptor.rsa_private_key = self.server_encryption.rsa_private_key
                                
                                # Decrypt session key
                                client_encryptor.decrypt_session_key(encrypted_session_key)
                                
                                # Store encryption handler for this client
                                self.client_encryptors[username] = client_encryptor
                                print(f"[SERVER] ✅ Session key established with '{username}'")
                                
                                # Send ACK
                                ack_msg = Message.create_message(
                                    config.MSG_KEY_EXCHANGE,
                                    "SERVER",
                                    username,
                                    None,
                                    {"step": "complete"}
                                )
                                client_socket.send(ack_msg.encode())
                            else:
                                print(f"[SERVER ERROR] No encrypted session key received from '{username}'")
                                return None
                        else:
                            print(f"[SERVER ERROR] Invalid key exchange message from '{username}'")
                            return None
                    
                    time.sleep(0.5)
                    
                    print(f"[SERVER DEBUG] Checking offline messages for '{username}'")
                    self.send_offline_messages(username)
                    
                    return username
                    
                    time.sleep(0.5)
                    
                    print(f"[SERVER DEBUG] Checking offline messages for '{username}'")
                    self.send_offline_messages(username)
                    
                    return username
                    
        except Exception as e:
            print(f"[SERVER ERROR] Connection handling error: {e}")
            return None
    
    def handle_disconnect(self, username):
        """Handle client dis-connection"""
        with self.lock:
            if username in self.clients:
                del self.clients[username]
                print(f"[SERVER] '{username}' disconnected")

            # Clean up encryption handler
            if username in self.client_encryptors:
                del self.client_encryptors[username]
                print(f"[SERVER] Encryption handler removed for '{username}'")

    
    def send_encrypted_message(self, username, message_str):
        """
        Send encrypted message to a client
        """
        if username not in self.clients:
            return False
        
        try:
            client_socket = self.clients[username]
            
            # Encrypt message if encryption is enabled
            if config.USE_ENCRYPTION and username in self.client_encryptors:
                encrypted_msg = self.client_encryptors[username].encrypt_message(message_str)
                client_socket.send(encrypted_msg.encode())
            else:
                client_socket.send(message_str.encode())
            
            return True
        except Exception as e:
            print(f"[SERVER ERROR] Failed to send message to '{username}': {e}")
            return False
    
    def handle_private_message(self, message):
        """Handle private message with history storage"""
        sender = message.get('sender')
        receiver = message.get('receiver')
        text = message.get('text')
        
        print(f"[SERVER] Private message from '{sender}' to '{receiver}': {text}")
        
        with self.lock:
            # CHECK IF RECEIVER EXISTS
            if not self.database.user_exists(receiver):
                print(f"[SERVER] User '{receiver}' does not exist")
                if sender in self.clients:
                    error_msg = Message.create_error_message(
                        f"❌ User '{receiver}' does not exist. Cannot send message."
                    )
                    self.send_encrypted_message(sender, error_msg)
                return
            
            # STORE MESSAGE IN HISTORY (for conversation threading)
            self.database.store_message(
                sender=sender,
                receiver=receiver,
                message_text=text,
                message_type=config.MSG_PRIVATE
            )
            
            if receiver in self.clients:
                try:
                    # Send message to receiver (encrypted)
                    self.send_encrypted_message(receiver, json.dumps(message))
                    
                    # Send confirmation to sender (encrypted)
                    if sender in self.clients:
                        confirm_msg = Message.create_success_message(
                            f"Message delivered to {receiver}"
                        )
                        self.send_encrypted_message(sender, confirm_msg)
                
                except Exception as e:
                    print(f"[SERVER ERROR] Failed to deliver message: {e}")
            
            else:
                print(f"[SERVER] '{receiver}' is offline. Storing message.")
                self.database.store_offline_message(
                    receiver, sender, config.MSG_PRIVATE, json.dumps(message)
                )
                
                sender_socket = self.clients.get(sender)
                if sender_socket:
                    offline_msg = Message.create_message(
                        config.MSG_OFFLINE,
                        "SERVER",
                        sender,
                        f"📬 '{receiver}' is offline. Message will be delivered when they connect."
                    )
                    sender_socket.send(offline_msg.encode())
    
    def handle_group_message(self, message):
        """Handle group message with offline support and history"""
        sender = message.get('sender')
        group_name = message.get('receiver')
        text = message.get('text')
        
        print(f"[SERVER] Group message from '{sender}' to '{group_name}': {text}")
        
        with self.lock:
            if group_name not in self.groups:
                print(f"[SERVER] Group '{group_name}' not found")
                return
            
            # STORE IN HISTORY
            self.database.store_message(
                sender=sender,
                receiver=group_name,
                message_text=text,
                message_type=config.MSG_GROUP,
                is_group=True,
                group_name=group_name
            )
            
            members = self.groups.get(group_name, set())
            db_members = self.database.get_group_members(group_name)
            members = members.union(set(db_members))
            
            delivered_count = 0
            offline_count = 0
            
            for member in members:
                if member == sender:
                    continue
                
                if member in self.clients:
                    try:
                        self.send_encrypted_message(member, json.dumps(message))
                        delivered_count += 1
                    except Exception as e:
                        print(f"[SERVER ERROR] Failed to deliver to '{member}': {e}")
                else:
                    if self.database.user_exists(member):
                        self.database.store_offline_message(
                            receiver=member,
                            sender=sender,
                            message_type=config.MSG_GROUP,
                            content=json.dumps(message),
                            is_group=True,
                            group_name=group_name
                        )
                        offline_count += 1
            
            print(f"[SERVER] Group message: {delivered_count} online, {offline_count} offline")
    
    def handle_history_request(self, message):
        """Handle conversation history request"""
        requester = message.get('sender')
        other_user = message['data'].get('other_user')
        is_group = message['data'].get('is_group', False)
        
        print(f"[SERVER] History request from '{requester}' for '{other_user}'")
        
        with self.lock:
            if is_group:
                history = self.database.get_group_history(other_user, limit=config.HISTORY_MESSAGE_LIMIT)
            else:
                history = self.database.get_conversation_history(requester, other_user, 
                                                                limit=config.HISTORY_MESSAGE_LIMIT)
            
            if requester in self.clients:
                response = Message.create_message(
                    config.MSG_HISTORY_RESPONSE,
                    "SERVER",
                    requester,
                    None,
                    {
                        'other_user': other_user,
                        'is_group': is_group,
                        'messages': history
                    }
                )
                self.send_encrypted_message(requester, response)
                print(f"[SERVER] Sent {len(history)} messages to '{requester}'")
    
    def handle_file_transfer(self, message):
        """Handle file transfer"""
        sender = message.get('sender')
        receiver = message.get('receiver')
        is_group = message.get('is_group', False)
        
        with self.lock:
            if is_group:
                if receiver in self.groups:
                    for member in self.groups[receiver]:
                        if member != sender and member in self.clients:
                            try:
                                self.send_encrypted_message(member, json.dumps(message))
                            except Exception as e:
                                print(f"[SERVER ERROR] File transfer to {member} failed: {e}")
            else:
                if receiver in self.clients:
                    try:
                        self.send_encrypted_message(receiver, json.dumps(message))
                    except Exception as e:
                        print(f"[SERVER ERROR] File transfer failed: {e}")
    
    def handle_create_group(self, message):
        """Handle group creation"""
        username = message.get('sender')
        group_name = message['data']['group_name']
        
        with self.lock:
            if self.database.create_group(group_name, username):
                self.groups[group_name] = {username}
                print(f"[SERVER] Group '{group_name}' created by '{username}'")
                
                if username in self.clients:
                    success_msg = Message.create_success_message(
                        f"Group '{group_name}' created successfully"
                    )
                    self.send_encrypted_message(username, success_msg)
            else:
                if username in self.clients:
                    error_msg = Message.create_error_message(
                        f"Group '{group_name}' already exists"
                    )
                    self.send_encrypted_message(username, error_msg)
    
    def handle_join_group(self, message):
        """Handle user joining group"""
        username = message.get('sender')
        group_name = message['data']['group_name']
        
        with self.lock:
            if group_name not in self.groups:
                self.groups[group_name] = set()
            
            self.groups[group_name].add(username)
            self.database.add_group_member(group_name, username)
        
        print(f"[SERVER] '{username}' joined group '{group_name}'")
        
        if username in self.clients:
            success_msg = Message.create_success_message(
                f"Joined group '{group_name}'"
            )
            self.send_encrypted_message(username, success_msg)
    
    def handle_list_users(self, username):
        """Send list of online users"""
        with self.lock:
            users = [{'username': user, 'status': 'online'} for user in self.clients.keys()]
        
        if username in self.clients:
            response = Message.create_message(
                config.MSG_LIST_USERS,
                "SERVER",
                username,
                None,
                {'users': users}
            )
            self.send_encrypted_message(username, response)
    
    def handle_list_groups(self, username):
        """Send list of available groups"""
        groups = self.database.get_all_groups()
        
        if username in self.clients:
            response = Message.create_message(
                config.MSG_LIST_GROUPS,
                "SERVER",
                username,
                None,
                {'groups': groups}
            )
            self.send_encrypted_message(username, response)
    
    def send_offline_messages(self, username):
        """Send stored offline messages"""
        messages = self.database.get_offline_messages(username)
        
        if messages:
            print(f"[SERVER] Sending {len(messages)} offline messages to '{username}'")
            
            if username in self.clients:
                notification_msg = Message.create_message(
                    config.MSG_OFFLINE,
                    "SERVER",
                    username,
                    f"You have {len(messages)} offline message(s)"
                )
                try:
                    self.send_encrypted_message(username, notification_msg)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"[SERVER ERROR] Failed to send notification: {e}")
                
                sent_count = 0
                for i, msg in enumerate(messages):
                    try:
                        self.send_encrypted_message(username, msg['content'])
                        sent_count += 1
                        
                        if i < len(messages) - 1:
                            time.sleep(0.2)
                        
                    except Exception as e:
                        print(f"[SERVER ERROR] Failed to send offline message {i+1}: {e}")
                        break
                
                if sent_count == len(messages):
                    self.database.mark_messages_delivered(username)
        else:
            print(f"[SERVER] No offline messages for '{username}'")
    
    def shutdown(self):
        """Shutdown server"""
        print("[SERVER] Shutting down...")
        self.running = False
        
        with self.lock:
            for client_socket in self.clients.values():
                try:
                    client_socket.close()
                except:
                    pass
        
        if self.server_socket:
            self.server_socket.close()


def main():
    server = ClassChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
