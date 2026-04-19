# Advanced Credential Management System

Enterprise-grade credential management with multi-service support, GitHub verification, and audit logging.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Manus Master Automation                   │
│                   Credential Management Hub                  │
└──────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    ┌───▼────┐           ┌────▼────┐          ┌────▼────┐
    │ GitHub │           │ Vault   │          │ Audit   │
    │ Verify │           │ Storage │          │ Logs    │
    └────────┘           └─────────┘          └─────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Service Layer    │
                    │  (Stripe, AWS,    │
                    │   Google, etc.)   │
                    └───────────────────┘
```

## Credential Types & Storage

### Type 1: Publishable Keys
- **Visibility**: Can be exposed in frontend code
- **Risk Level**: Low
- **Rotation**: Quarterly
- **Storage**: L1 Cache + L2 Database
- **Examples**: Stripe Publishable Key, Google Analytics ID

```typescript
interface PublishableKey {
  id: string;
  service: string;
  key: string;
  environment: 'dev' | 'staging' | 'production';
  createdAt: Date;
  expiresAt: Date;
  lastUsed: Date;
  usageCount: number;
}
```

### Type 2: Secret Keys
- **Visibility**: Must never be exposed
- **Risk Level**: Critical
- **Rotation**: Monthly
- **Storage**: L2 Encrypted Database + L3 Vault
- **Examples**: Stripe Secret Key, AWS Access Key, OpenAI API Key

```typescript
interface SecretKey {
  id: string;
  service: string;
  keyType: 'secret' | 'token' | 'password';
  encryptedValue: string; // AES-256 encrypted
  environment: 'dev' | 'staging' | 'production';
  createdAt: Date;
  expiresAt: Date;
  rotationSchedule: 'weekly' | 'monthly' | 'quarterly';
  lastRotated: Date;
  accessLog: AccessLog[];
  mastery: 'developer' | 'expert' | 'master';
}
```

### Type 3: Webhook Secrets
- **Visibility**: Shared between Manus and external service
- **Risk Level**: High
- **Rotation**: On-demand
- **Storage**: L2 Encrypted Database
- **Examples**: Stripe Webhook Secret, GitHub Webhook Secret

```typescript
interface WebhookSecret {
  id: string;
  service: string;
  webhookUrl: string;
  encryptedSecret: string;
  events: string[]; // ['payment.success', 'customer.created']
  active: boolean;
  createdAt: Date;
  lastTriggered: Date;
  failureCount: number;
}
```

## GitHub Mastery Verification

### Verification Flow

```
1. User initiates: manus-master-automation verify-github USERNAME
   │
2. System fetches GitHub profile data
   ├─ Public repos count
   ├─ Total commits
   ├─ Contribution graph
   ├─ Follower count
   └─ Verified status
   │
3. Calculate mastery level
   ├─ Beginner: No requirements
   ├─ Developer: 5+ repos, 50+ commits
   ├─ Expert: 20+ repos, 500+ commits
   └─ Master: 50+ repos, 2000+ commits
   │
4. Issue access token (valid 24 hours)
   │
5. Log verification event
   └─ Timestamp, username, level, IP address
```

### Verification Script

```python
#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta

class GitHubVerifier:
    def __init__(self, github_token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}" if github_token else "",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def verify_user(self, username):
        """Verify GitHub user and determine mastery level"""
        
        # Fetch user profile
        user_response = requests.get(
            f"{self.base_url}/users/{username}",
            headers=self.headers
        )
        
        if user_response.status_code != 200:
            return {"error": "User not found"}
        
        user_data = user_response.json()
        
        # Fetch repositories
        repos_response = requests.get(
            f"{self.base_url}/users/{username}/repos?per_page=100",
            headers=self.headers
        )
        
        repos = repos_response.json()
        repo_count = len(repos)
        
        # Calculate total commits
        total_commits = 0
        for repo in repos:
            commits_response = requests.get(
                f"{self.base_url}/repos/{username}/{repo['name']}/commits?per_page=1",
                headers=self.headers
            )
            if commits_response.status_code == 200:
                # GitHub returns commit count in Link header
                link_header = commits_response.headers.get('Link', '')
                if 'last' in link_header:
                    # Extract page number from last link
                    import re
                    match = re.search(r'page=(\d+)', link_header)
                    if match:
                        total_commits += int(match.group(1))
        
        # Determine mastery level
        mastery = self._calculate_mastery(repo_count, total_commits, user_data)
        
        return {
            "username": username,
            "verified": True,
            "profile_url": user_data['html_url'],
            "repositories": repo_count,
            "commits": total_commits,
            "followers": user_data['followers'],
            "verified_badge": user_data.get('verified', False),
            "mastery_level": mastery['level'],
            "access_token_valid_until": (
                datetime.now() + timedelta(hours=24)
            ).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_mastery(self, repos, commits, user_data):
        """Calculate mastery level based on GitHub metrics"""
        
        if repos >= 50 and commits >= 2000 and user_data.get('verified'):
            return {"level": "master", "score": 100}
        elif repos >= 20 and commits >= 500:
            return {"level": "expert", "score": 75}
        elif repos >= 5 and commits >= 50:
            return {"level": "developer", "score": 50}
        else:
            return {"level": "beginner", "score": 0}
```

## Multi-Service Integration

### Service Registry

```typescript
interface ServiceRegistry {
  stripe: {
    keys: ['publishable_key', 'secret_key', 'webhook_secret'],
    rotationSchedule: 'monthly',
    rateLimit: 100,
    mastery: 'developer'
  },
  paypal: {
    keys: ['client_id', 'secret', 'signature'],
    rotationSchedule: 'quarterly',
    rateLimit: 50,
    mastery: 'developer'
  },
  aws: {
    keys: ['access_key_id', 'secret_access_key', 'session_token'],
    rotationSchedule: 'monthly',
    rateLimit: 1000,
    mastery: 'expert'
  },
  openai: {
    keys: ['api_key', 'organization_id'],
    rotationSchedule: 'quarterly',
    rateLimit: 500,
    mastery: 'developer'
  },
  google_workspace: {
    keys: ['oauth_credentials', 'service_account_json'],
    rotationSchedule: 'quarterly',
    rateLimit: 1000,
    mastery: 'expert'
  },
  // ... 50+ more services
}
```

### Adding New Service

```typescript
// 1. Register service
await credentialManager.registerService({
  name: 'my-api',
  keys: ['api_key', 'api_secret'],
  rotationSchedule: 'monthly',
  rateLimit: 100,
  mastery: 'developer',
  documentation: 'https://docs.myapi.com/auth'
});

// 2. Add credentials
await credentialManager.add('my-api', {
  api_key: 'pk_test_...',
  api_secret: 'sk_test_...',
  environment: 'development'
});

// 3. Use in code
const apiKey = await credentialManager.get('my-api.api_key');
```

## Audit Logging

### Audit Log Schema

```typescript
interface AuditLog {
  id: string;
  timestamp: Date;
  action: 'create' | 'read' | 'update' | 'delete' | 'rotate';
  credentialId: string;
  service: string;
  userId: string;
  userMastery: string;
  ipAddress: string;
  userAgent: string;
  result: 'success' | 'failure';
  errorMessage?: string;
  metadata: {
    environment: string;
    duration: number; // milliseconds
    dataSize: number;
  };
}
```

### Querying Audit Logs

```typescript
// Get all access to Stripe secret key
const logs = await credentialManager.auditLog({
  credentialId: 'stripe.secret_key',
  action: 'read',
  since: '7 days ago'
});

// Find suspicious activity
const suspicious = await credentialManager.auditLog({
  filters: {
    result: 'failure',
    failureCount: { $gt: 3 },
    timeWindow: '1 hour'
  }
});

// Export for compliance
const report = await credentialManager.exportAuditReport({
  startDate: '2026-01-01',
  endDate: '2026-03-31',
  format: 'csv'
});
```

## Rotation Strategies

### Automatic Rotation

```typescript
// Schedule automatic rotation
await credentialManager.scheduleRotation({
  credentialId: 'stripe.secret_key',
  schedule: 'monthly',
  notifyBefore: '7 days',
  autoUpdate: true // Update all services using this key
});

// Rotation process
1. Generate new credential
2. Notify user of pending rotation
3. Update all services (with fallback to old key)
4. Monitor for errors (24-hour window)
5. Archive old credential
6. Log rotation event
```

### Manual Rotation

```typescript
// Manually rotate credential
const newKey = await credentialManager.rotate('stripe.secret_key', {
  reason: 'suspected compromise',
  immediate: true,
  notifyServices: true
});

// Returns new key for manual update if needed
```

## Access Control Policies

### Role-Based Access

```typescript
const policies = {
  beginner: {
    canRead: ['public_keys'],
    canCreate: false,
    canRotate: false,
    canDelete: false,
    canAudit: false
  },
  developer: {
    canRead: ['public_keys', 'own_secret_keys'],
    canCreate: ['own_credentials'],
    canRotate: ['own_credentials'],
    canDelete: false,
    canAudit: ['own_credentials']
  },
  expert: {
    canRead: ['all_keys'],
    canCreate: ['all_credentials'],
    canRotate: ['all_credentials'],
    canDelete: ['archived_credentials'],
    canAudit: ['all_credentials'],
    canManageUsers: true
  },
  master: {
    canRead: ['all_keys'],
    canCreate: ['all_credentials'],
    canRotate: ['all_credentials'],
    canDelete: ['all_credentials'],
    canAudit: ['all_credentials'],
    canManageUsers: true,
    canManageServices: true
  }
};
```

## Security Best Practices

### Encryption

```typescript
// All secret keys encrypted with AES-256-GCM
const encrypted = await encrypt(secretKey, {
  algorithm: 'aes-256-gcm',
  keyDerivation: 'pbkdf2',
  iterations: 100000,
  salt: generateRandomSalt(32)
});

// Decryption only in secure context
const decrypted = await decrypt(encrypted, {
  masterKey: loadMasterKeyFromVault(),
  verifyIntegrity: true
});
```

### Rate Limiting

```typescript
// Prevent brute force attacks
const rateLimiter = new RateLimiter({
  maxRequests: 10,
  windowMs: 60000, // 1 minute
  keyGenerator: (req) => req.user.id + req.ip
});

// Exponential backoff on failure
const backoff = new ExponentialBackoff({
  initialDelay: 1000,
  maxDelay: 60000,
  multiplier: 2
});
```

### IP Whitelisting (Enterprise)

```typescript
// Restrict credential access to specific IPs
await credentialManager.setIpWhitelist('stripe.secret_key', {
  ips: ['192.168.1.0/24', '10.0.0.0/8'],
  enforcement: 'strict' // Deny all others
});
```

## Monitoring & Alerts

### Real-Time Monitoring

```typescript
// Monitor for anomalies
const monitor = new CredentialMonitor({
  alerts: [
    {
      name: 'unusual_access_pattern',
      condition: 'accessCount > 100 in 1 hour',
      action: 'notify_admin'
    },
    {
      name: 'failed_rotation',
      condition: 'rotation failed 3 times',
      action: 'revoke_credential'
    },
    {
      name: 'expiration_warning',
      condition: 'credential expires in 7 days',
      action: 'notify_user'
    }
  ]
});
```

### Compliance Reports

```typescript
// Generate compliance report
const report = await credentialManager.generateComplianceReport({
  period: 'quarterly',
  includeAuditLog: true,
  includeRotationHistory: true,
  format: 'pdf'
});
```
