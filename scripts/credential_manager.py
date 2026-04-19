#!/usr/bin/env python3
"""
Master Automation Engine - Credential Manager
Advanced credential management with encryption, rotation, and audit logging
"""

import json
import os
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from cryptography.fernet import Fernet
import sqlite3

class MasteryLevel(Enum):
    """GitHub-based mastery levels"""
    BEGINNER = "beginner"
    DEVELOPER = "developer"
    EXPERT = "expert"
    MASTER = "master"

@dataclass
class GitHubProfile:
    """GitHub user profile data"""
    username: str
    repositories: int
    commits: int
    followers: int
    verified: bool
    mastery_level: MasteryLevel
    profile_url: str

@dataclass
class Credential:
    """Credential object"""
    id: str
    service: str
    key_type: str  # 'publishable', 'secret', 'webhook'
    value: str  # Encrypted
    environment: str  # 'dev', 'staging', 'production'
    created_at: datetime
    expires_at: Optional[datetime]
    rotation_schedule: str  # 'weekly', 'monthly', 'quarterly'
    last_rotated: Optional[datetime]
    mastery_required: MasteryLevel

class CredentialManager:
    """Enterprise credential management system"""
    
    def __init__(self, db_path: str = "/tmp/manus_credentials.db"):
        self.db_path = db_path
        self.encryption_key = self._load_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self._init_database()
    
    def _load_or_create_encryption_key(self) -> bytes:
        """Load or create encryption key"""
        key_path = os.path.expanduser("~/.manus/encryption.key")
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            os.chmod(key_path, 0o600)
            return key
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Credentials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id TEXT PRIMARY KEY,
                service TEXT NOT NULL,
                key_type TEXT NOT NULL,
                encrypted_value TEXT NOT NULL,
                environment TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                rotation_schedule TEXT,
                last_rotated TEXT,
                mastery_required TEXT,
                UNIQUE(service, key_type, environment)
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                credential_id TEXT NOT NULL,
                service TEXT NOT NULL,
                user_id TEXT NOT NULL,
                user_mastery TEXT NOT NULL,
                ip_address TEXT,
                result TEXT,
                error_message TEXT,
                FOREIGN KEY(credential_id) REFERENCES credentials(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def verify_github_user(self, username: str, token: Optional[str] = None) -> GitHubProfile:
        """Verify GitHub user and determine mastery level"""
        
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
        
        # Fetch user profile
        user_response = requests.get(
            f'https://api.github.com/users/{username}',
            headers=headers
        )
        
        if user_response.status_code != 200:
            raise ValueError(f"GitHub user not found: {username}")
        
        user_data = user_response.json()
        
        # Fetch repositories
        repos_response = requests.get(
            f'https://api.github.com/users/{username}/repos?per_page=100',
            headers=headers
        )
        
        repos = repos_response.json()
        repo_count = len(repos)
        
        # Calculate total commits (simplified)
        total_commits = sum(repo.get('size', 0) for repo in repos) // 100
        
        # Determine mastery level
        mastery = self._calculate_mastery(repo_count, total_commits, user_data)
        
        return GitHubProfile(
            username=username,
            repositories=repo_count,
            commits=total_commits,
            followers=user_data.get('followers', 0),
            verified=user_data.get('verified', False),
            mastery_level=mastery,
            profile_url=user_data.get('html_url', '')
        )
    
    def _calculate_mastery(self, repos: int, commits: int, user_data: Dict) -> MasteryLevel:
        """Calculate mastery level based on GitHub metrics"""
        
        if repos >= 50 and commits >= 2000 and user_data.get('verified'):
            return MasteryLevel.MASTER
        elif repos >= 20 and commits >= 500:
            return MasteryLevel.EXPERT
        elif repos >= 5 and commits >= 50:
            return MasteryLevel.DEVELOPER
        else:
            return MasteryLevel.BEGINNER
    
    def add_credential(
        self,
        service: str,
        key_type: str,
        value: str,
        environment: str = 'development',
        expires_in_days: Optional[int] = None,
        rotation_schedule: str = 'monthly',
        mastery_required: MasteryLevel = MasteryLevel.DEVELOPER
    ) -> str:
        """Add new credential"""
        
        credential_id = f"{service}.{key_type}.{environment}"
        
        # Encrypt value
        encrypted_value = self.cipher.encrypt(value.encode()).decode()
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO credentials (
                    id, service, key_type, encrypted_value, environment,
                    created_at, expires_at, rotation_schedule, mastery_required
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                credential_id,
                service,
                key_type,
                encrypted_value,
                environment,
                datetime.now().isoformat(),
                expires_at,
                rotation_schedule,
                mastery_required.value
            ))
            
            conn.commit()
            
            # Log action
            self._log_action(
                action='create',
                credential_id=credential_id,
                service=service,
                result='success'
            )
            
            return credential_id
        
        except sqlite3.IntegrityError:
            raise ValueError(f"Credential already exists: {credential_id}")
        finally:
            conn.close()
    
    def get_credential(
        self,
        service: str,
        key_type: str,
        environment: str = 'development',
        user_mastery: MasteryLevel = MasteryLevel.BEGINNER
    ) -> str:
        """Retrieve and decrypt credential"""
        
        credential_id = f"{service}.{key_type}.{environment}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT encrypted_value, mastery_required, expires_at FROM credentials WHERE id = ?',
            (credential_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ValueError(f"Credential not found: {credential_id}")
        
        encrypted_value, mastery_required, expires_at = row
        
        # Check mastery level
        required_mastery = MasteryLevel(mastery_required)
        mastery_levels = [MasteryLevel.BEGINNER, MasteryLevel.DEVELOPER, MasteryLevel.EXPERT, MasteryLevel.MASTER]
        
        if mastery_levels.index(user_mastery) < mastery_levels.index(required_mastery):
            raise PermissionError(f"Insufficient mastery level. Required: {required_mastery.value}")
        
        # Check expiration
        if expires_at:
            if datetime.fromisoformat(expires_at) < datetime.now():
                raise ValueError(f"Credential expired: {credential_id}")
        
        # Decrypt value
        decrypted_value = self.cipher.decrypt(encrypted_value.encode()).decode()
        
        # Log action
        self._log_action(
            action='read',
            credential_id=credential_id,
            service=service,
            result='success'
        )
        
        return decrypted_value
    
    def rotate_credential(
        self,
        service: str,
        key_type: str,
        new_value: str,
        environment: str = 'development',
        reason: str = 'scheduled'
    ) -> str:
        """Rotate credential"""
        
        credential_id = f"{service}.{key_type}.{environment}"
        
        # Archive old credential
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current credential
        cursor.execute(
            'SELECT * FROM credentials WHERE id = ?',
            (credential_id,)
        )
        
        old_credential = cursor.fetchone()
        
        if not old_credential:
            raise ValueError(f"Credential not found: {credential_id}")
        
        # Encrypt new value
        encrypted_value = self.cipher.encrypt(new_value.encode()).decode()
        
        # Update credential
        cursor.execute('''
            UPDATE credentials
            SET encrypted_value = ?, last_rotated = ?
            WHERE id = ?
        ''', (encrypted_value, datetime.now().isoformat(), credential_id))
        
        conn.commit()
        conn.close()
        
        # Log action
        self._log_action(
            action='rotate',
            credential_id=credential_id,
            service=service,
            result='success'
        )
        
        return credential_id
    
    def list_credentials(
        self,
        service: Optional[str] = None,
        environment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all credentials (without values)"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT id, service, key_type, environment, created_at, expires_at, mastery_required FROM credentials WHERE 1=1'
        params = []
        
        if service:
            query += ' AND service = ?'
            params.append(service)
        
        if environment:
            query += ' AND environment = ?'
            params.append(environment)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        credentials = []
        for row in rows:
            credentials.append({
                'id': row[0],
                'service': row[1],
                'key_type': row[2],
                'environment': row[3],
                'created_at': row[4],
                'expires_at': row[5],
                'mastery_required': row[6]
            })
        
        return credentials
    
    def get_audit_log(
        self,
        credential_id: Optional[str] = None,
        action: Optional[str] = None,
        since_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM audit_log WHERE timestamp > datetime("now", "-' + str(since_hours) + ' hours")'
        params = []
        
        if credential_id:
            query += ' AND credential_id = ?'
            params.append(credential_id)
        
        if action:
            query += ' AND action = ?'
            params.append(action)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                'id': row[0],
                'timestamp': row[1],
                'action': row[2],
                'credential_id': row[3],
                'service': row[4],
                'user_id': row[5],
                'user_mastery': row[6],
                'ip_address': row[7],
                'result': row[8],
                'error_message': row[9]
            })
        
        return logs
    
    def _log_action(
        self,
        action: str,
        credential_id: str,
        service: str,
        result: str,
        error_message: Optional[str] = None,
        user_id: str = 'system',
        user_mastery: str = 'master'
    ):
        """Log credential action to audit log"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log (
                timestamp, action, credential_id, service, user_id, user_mastery,
                result, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            action,
            credential_id,
            service,
            user_id,
            user_mastery,
            result,
            error_message
        ))
        
        conn.commit()
        conn.close()

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manus Credential Manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Verify GitHub
    verify_parser = subparsers.add_parser('verify-github', help='Verify GitHub user')
    verify_parser.add_argument('username', help='GitHub username')
    verify_parser.add_argument('--token', help='GitHub API token')
    
    # Add credential
    add_parser = subparsers.add_parser('add', help='Add credential')
    add_parser.add_argument('service', help='Service name')
    add_parser.add_argument('key_type', help='Key type (publishable/secret/webhook)')
    add_parser.add_argument('value', help='Credential value')
    add_parser.add_argument('--env', default='development', help='Environment')
    add_parser.add_argument('--expires-in-days', type=int, help='Expiration in days')
    
    # Get credential
    get_parser = subparsers.add_parser('get', help='Get credential')
    get_parser.add_argument('service', help='Service name')
    get_parser.add_argument('key_type', help='Key type')
    get_parser.add_argument('--env', default='development', help='Environment')
    
    # List credentials
    list_parser = subparsers.add_parser('list', help='List credentials')
    list_parser.add_argument('--service', help='Filter by service')
    list_parser.add_argument('--env', help='Filter by environment')
    
    # Audit log
    audit_parser = subparsers.add_parser('audit', help='View audit log')
    audit_parser.add_argument('--credential-id', help='Filter by credential ID')
    audit_parser.add_argument('--action', help='Filter by action')
    audit_parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    
    args = parser.parse_args()
    
    manager = CredentialManager()
    
    if args.command == 'verify-github':
        profile = manager.verify_github_user(args.username, args.token)
        print(json.dumps(asdict(profile), default=str, indent=2))
    
    elif args.command == 'add':
        cred_id = manager.add_credential(
            service=args.service,
            key_type=args.key_type,
            value=args.value,
            environment=args.env,
            expires_in_days=args.expires_in_days
        )
        print(f"✓ Credential added: {cred_id}")
    
    elif args.command == 'get':
        value = manager.get_credential(
            service=args.service,
            key_type=args.key_type,
            environment=args.env
        )
        print(value)
    
    elif args.command == 'list':
        credentials = manager.list_credentials(
            service=args.service,
            environment=args.env
        )
        print(json.dumps(credentials, indent=2))
    
    elif args.command == 'audit':
        logs = manager.get_audit_log(
            credential_id=args.credential_id,
            action=args.action,
            since_hours=args.hours
        )
        print(json.dumps(logs, indent=2))

if __name__ == '__main__':
    main()
