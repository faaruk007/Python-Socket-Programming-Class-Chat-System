"""
Enhanced Database module with Message History
Stores ALL messages for conversation thread persistence
"""

import sqlite3
import json
from datetime import datetime
import config


class MessageDatabase:
    """Handles message history, offline messages, users and groups"""
    
    def __init__(self, db_file=config.DB_FILE):
        """Initialize database connection"""
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create registered users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                registered_at TEXT NOT NULL,
                last_seen TEXT
            )
        ''')
        
        # Create message history table (NEW - stores ALL messages)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                message_type TEXT NOT NULL,
                message_text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                is_group INTEGER DEFAULT 0,
                group_name TEXT
            )
        ''')
        
        # Create offline messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receiver TEXT NOT NULL,
                sender TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                delivered INTEGER DEFAULT 0,
                is_group INTEGER DEFAULT 0,
                group_name TEXT
            )
        ''')
        
        # Create groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT UNIQUE NOT NULL,
                creator TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Create group members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                username TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                UNIQUE(group_name, username)
            )
        ''')
        
        # Create index for faster message history queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_message_history_users 
            ON message_history(sender, receiver, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print("[DATABASE] Database initialized with message history support")
    
    def register_user(self, username):
        """Register a new user or update last_seen"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            timestamp = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users (username, registered_at, last_seen)
                VALUES (?, ?, ?)
            ''', (username, timestamp, timestamp))
            conn.commit()
            print(f"[DATABASE] User '{username}' registered")
        except sqlite3.IntegrityError:
            # User exists, update last_seen
            cursor.execute('''
                UPDATE users SET last_seen = ? WHERE username = ?
            ''', (datetime.now().isoformat(), username))
            conn.commit()
        
        conn.close()
        return True
    
    def user_exists(self, username):
        """Check if user is registered"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def store_message(self, sender, receiver, message_text, message_type=config.MSG_PRIVATE, 
                     is_group=False, group_name=None):
        """
        Store a message in history (for ALL messages, not just offline)
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO message_history 
            (sender, receiver, message_type, message_text, timestamp, is_group, group_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sender, receiver, message_type, message_text, timestamp, 
              1 if is_group else 0, group_name))
        
        conn.commit()
        conn.close()
        print(f"[DATABASE] Stored message: {sender} -> {receiver}")
    
    def get_conversation_history(self, user1, user2, limit=20):
        """
        Get conversation history between two users
        
        Args:
            user1: First user
            user2: Second user  
            limit: Maximum number of messages to retrieve (default 20)
            
        Returns:
            List of messages ordered by timestamp
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get messages where user1 and user2 are involved (bidirectional)
        cursor.execute('''
            SELECT sender, receiver, message_text, timestamp, message_type
            FROM message_history
            WHERE is_group = 0 AND (
                (sender = ? AND receiver = ?) OR
                (sender = ? AND receiver = ?)
            )
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user1, user2, user2, user1, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'sender': row[0],
                'receiver': row[1],
                'text': row[2],
                'timestamp': row[3],
                'type': row[4]
            })
        
        # Reverse to show oldest first
        messages.reverse()
        
        conn.close()
        print(f"[DATABASE] Retrieved {len(messages)} messages for conversation {user1} <-> {user2}")
        return messages
    
    def get_group_history(self, group_name, limit=20):
        """Get message history for a group"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sender, message_text, timestamp
            FROM message_history
            WHERE is_group = 1 AND group_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (group_name, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'sender': row[0],
                'text': row[1],
                'timestamp': row[2]
            })
        
        messages.reverse()
        
        conn.close()
        print(f"[DATABASE] Retrieved {len(messages)} messages for group {group_name}")
        return messages
    
    def store_offline_message(self, receiver, sender, message_type, content, 
                             is_group=False, group_name=None):

        """Store an offline message"""
        print(f"[DATABASE DEBUG] Storing offline message: {sender} -> {receiver}" + 
              (f" (Group: {group_name})" if is_group else ""))
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO offline_messages 
            (receiver, sender, message_type, content, timestamp, is_group, group_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (receiver, sender, message_type, content, timestamp, 
              1 if is_group else 0, group_name))
        
        conn.commit()
        cursor.execute('SELECT COUNT(*) FROM offline_messages WHERE receiver = ? AND delivered = 0', 
                      (receiver,))
        count = cursor.fetchone()[0]
        print(f"[DATABASE DEBUG] Total undelivered messages for '{receiver}': {count}")
        
        conn.close()
    
    def get_offline_messages(self, username):
        """Retrieve all offline messages for a user"""
        print(f"[DATABASE DEBUG] Retrieving offline messages for '{username}'")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, sender, message_type, content, timestamp
            FROM offline_messages
            WHERE receiver = ? AND delivered = 0
            ORDER BY timestamp
        ''', (username,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'sender': row[1],
                'type': row[2],
                'content': row[3],
                'timestamp': row[4]
            })
            print(f"[DATABASE DEBUG] Retrieved message ID {row[0]} from {row[1]}")
        
        print(f"[DATABASE DEBUG] Total messages retrieved: {len(messages)}")
        conn.close()
        return messages
    
    def mark_messages_delivered(self, username):
        """Mark all messages for a user as delivered"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE offline_messages
            SET delivered = 1
            WHERE receiver = ? AND delivered = 0
        ''', (username,))
        
        conn.commit()
        conn.close()
    
    def create_group(self, group_name, creator):
        """Create a new group"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO groups (group_name, creator, created_at)
                VALUES (?, ?, ?)
            ''', (group_name, creator, timestamp))
            
            cursor.execute('''
                INSERT INTO group_members (group_name, username, joined_at)
                VALUES (?, ?, ?)
            ''', (group_name, creator, timestamp))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def add_group_member(self, group_name, username):
        """Add a user to a group"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            timestamp = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO group_members (group_name, username, joined_at)
                VALUES (?, ?, ?)
            ''', (group_name, username, timestamp))
            conn.commit()
            print(f"[DATABASE] Added '{username}' to group '{group_name}'")
        except sqlite3.IntegrityError:
            print(f"[DATABASE] '{username}' already in group '{group_name}'")
        
        conn.close()
    
    def get_group_members(self, group_name):
        """Get all members of a group"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username FROM group_members WHERE group_name = ?
        ''', (group_name,))
        
        members = [row[0] for row in cursor.fetchall()]
        conn.close()
        return members
    
    def get_all_groups(self):
        """Get all groups"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT group_name, creator FROM groups')
        groups = [{'name': row[0], 'creator': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return groups
    
    def is_group_member(self, group_name, username):
        """Check if user is a member of a group"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*)
            FROM group_members
            WHERE group_name = ? AND username = ?
        ''', (group_name, username))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def get_all_users(self):
        """Get all registered users"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT username, registered_at, last_seen FROM users ORDER BY username')
        users = cursor.fetchall()
        
        conn.close()
        return users
