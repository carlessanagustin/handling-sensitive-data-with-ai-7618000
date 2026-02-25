# 🔒 Security Features Documentation

This document details all security features implemented in this LiteLLM proxy setup for maximal data safety.

## Table of Contents

1. [Authentication & Authorization](#1-authentication--authorization)
2. [Data Encryption](#2-data-encryption)
3. [Network Security](#3-network-security)
4. [Container Security](#4-container-security)
5. [Database Security](#5-database-security)
6. [Rate Limiting & Abuse Prevention](#6-rate-limiting--abuse-prevention)
7. [Audit Logging & Monitoring](#7-audit-logging--monitoring)
8. [Privacy & Data Protection](#8-privacy--data-protection)
9. [Secure Configuration](#9-secure-configuration)
10. [Vulnerability Management](#10-vulnerability-management)

---

## 1. Authentication & Authorization

### ✅ Master Key Authentication
- **Feature**: Admin-level authentication using `LITELLM_MASTER_KEY`
- **Implementation**: Required for all administrative operations
- **Security**: Must start with `sk-` prefix, minimum 32 characters recommended
- **Scope**: Full proxy management, key generation, configuration changes

### ✅ Virtual Key System
- **Feature**: Generate temporary/scoped API keys for clients
- **Implementation**: Database-backed key management
- **Security**: Each key can have individual budgets, rate limits, and model access
- **Benefits**: Granular access control, easy revocation, usage tracking

### ✅ Team-Based Access Control
- **Feature**: Multi-tenant support with team isolation
- **Implementation**: `enable_team_based_routing: true`
- **Security**: Teams can only access their assigned models and budgets
- **Use Case**: Multi-department or multi-client deployments

### ✅ Disable Master Key Return
- **Feature**: Prevents master key from being returned in API responses
- **Implementation**: `disable_master_key_return: true`
- **Security**: Reduces risk of accidental key exposure in logs or responses

---

## 2. Data Encryption

### ✅ API Key Encryption at Rest
- **Feature**: All LLM provider API keys encrypted in database
- **Implementation**: Using `LITELLM_SALT_KEY` for encryption/decryption
- **Algorithm**: Industry-standard encryption (AES-256)
- **Critical**: Salt key cannot be changed after initial setup

### ✅ Database Connection Encryption
- **Feature**: SSL/TLS for PostgreSQL connections
- **Implementation**: `sslmode=prefer` in connection string
- **Security**: Prevents man-in-the-middle attacks on database traffic

### ✅ Password Hashing
- **Feature**: Secure password storage for database users
- **Implementation**: SCRAM-SHA-256 authentication method
- **Security**: Industry-standard cryptographic hashing

### ✅ Encrypted Redis Cache
- **Feature**: Password-protected Redis with authentication
- **Implementation**: `requirepass` configuration
- **Security**: Prevents unauthorized cache access

---

## 3. Network Security

### ✅ Isolated Docker Network
- **Feature**: Private bridge network for inter-container communication
- **Implementation**: `litellm_network` with custom subnet (172.28.0.0/16)
- **Security**: Services only accessible within the network, controlled external access

### ✅ Port Exposure Control
- **Feature**: Only proxy port (4000) exposed to host
- **Implementation**: Database and Redis not exposed externally
- **Security**: Reduces attack surface significantly

### ✅ CORS Configuration
- **Feature**: Strict Cross-Origin Resource Sharing controls
- **Implementation**: `ALLOWED_ORIGINS` environment variable
- **Security**: Prevents unauthorized web applications from accessing the API

### ✅ Security Headers
- **Feature**: HTTP security headers on all responses
- **Implementation**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000`
  - `Content-Security-Policy: default-src 'self'`
- **Security**: Protects against XSS, clickjacking, MIME sniffing attacks

### ✅ SSL/TLS Verification
- **Feature**: Verify SSL certificates for external API calls
- **Implementation**: `ssl_verify: true` (configurable)
- **Security**: Prevents man-in-the-middle attacks on LLM API calls

---

## 4. Container Security

### ✅ Non-Root User Execution
- **Feature**: All containers run as non-root users
- **Implementation**:
  - PostgreSQL: `user: postgres`
  - LiteLLM: `user: "1000:1000"`
  - Redis: `user: redis`
- **Security**: Limits damage from container escape vulnerabilities

### ✅ Read-Only Root Filesystem
- **Feature**: Container root filesystems mounted read-only
- **Implementation**: `read_only: true` with specific tmpfs mounts
- **Security**: Prevents malware from modifying system files

### ✅ Capability Dropping
- **Feature**: Drop all Linux capabilities
- **Implementation**: `cap_drop: - ALL`
- **Security**: Removes unnecessary privileges from containers

### ✅ No New Privileges
- **Feature**: Prevents privilege escalation
- **Implementation**: `security_opt: - no-new-privileges:true`
- **Security**: Blocks setuid/setgid binary exploitation

### ✅ Resource Limits
- **Feature**: CPU and memory limits per container
- **Implementation**: Deploy resource constraints optimized for M2 Max
- **Security**: Prevents resource exhaustion DoS attacks
- **Limits**:
  - PostgreSQL: 4 CPU cores, 4GB RAM
  - LiteLLM: 8 CPU cores, 16GB RAM
  - Redis: 2 CPU cores, 2GB RAM

### ✅ Health Checks
- **Feature**: Container health monitoring
- **Implementation**: Regular health check probes for all services
- **Security**: Automatic restart of unhealthy containers

---

## 5. Database Security

### ✅ Secure Authentication Method
- **Feature**: SCRAM-SHA-256 authentication (not MD5 or trust)
- **Implementation**: `POSTGRES_HOST_AUTH_METHOD=scram-sha-256`
- **Security**: Strong cryptographic authentication mechanism

### ✅ Database User Isolation
- **Feature**: Dedicated database user with limited privileges
- **Implementation**: `litellm_user` with schema-level permissions
- **Security**: Follows principle of least privilege

### ✅ Connection Pooling
- **Feature**: Limited connection pool with timeouts
- **Implementation**: `database_connection_pool_limit: 100`
- **Security**: Prevents connection exhaustion attacks

### ✅ Audit Logging
- **Feature**: Database-level audit trail
- **Implementation**: Trigger-based audit log for all table changes
- **Security**: Track all data modifications with timestamps and users

### ✅ Persistent Storage
- **Feature**: Named Docker volume for database data
- **Implementation**: `postgres_data` volume
- **Security**: Data survives container restarts, easier to backup

### ✅ Schema Isolation
- **Feature**: Separate schema for LiteLLM tables
- **Implementation**: `litellm` schema with controlled access
- **Security**: Logical separation from other database objects

---

## 6. Rate Limiting & Abuse Prevention

### ✅ Global Rate Limiting
- **Feature**: Proxy-wide request rate limits
- **Implementation**: `global_rate_limit_per_minute: 1000`
- **Security**: Prevents proxy-level DoS attacks

### ✅ Per-Key Rate Limiting
- **Feature**: RPM (Requests Per Minute) limits per virtual key
- **Implementation**: Set during key generation
- **Security**: Prevents individual key abuse

### ✅ TPM (Tokens Per Minute) Limits
- **Feature**: Token-based rate limiting per key
- **Implementation**: Configurable per virtual key
- **Security**: Prevents excessive token consumption

### ✅ Budget Controls
- **Feature**: Dollar-based spending limits per key/team
- **Implementation**: `max_budget` setting with real-time tracking
- **Security**: Prevents financial abuse and cost overruns

### ✅ Max Parallel Requests
- **Feature**: Concurrent request limits per key
- **Implementation**: Configurable in key generation
- **Security**: Prevents connection exhaustion

### ✅ Request Size Limits
- **Feature**: Maximum request payload size
- **Implementation**: `max_request_size_mb: 10`
- **Security**: Prevents memory exhaustion attacks

### ✅ Model Cooldown
- **Feature**: Temporary disable failed models
- **Implementation**: `cooldown_time: 60` seconds
- **Security**: Prevents repeated failures from degrading service

---

## 7. Audit Logging & Monitoring

### ✅ Comprehensive Request Logging
- **Feature**: Log all API requests
- **Implementation**: `LITELLM_REQUEST_LOGS: True`
- **Security**: Full audit trail of all proxy activity

### ✅ Store Audit Logs in Database
- **Feature**: Persistent audit logs
- **Implementation**: `store_audit_logs: true`
- **Security**: Tamper-resistant logging with database integrity

### ✅ Spend Tracking
- **Feature**: Track API costs per key/user/team
- **Implementation**: `disable_spend_logs: false`
- **Security**: Financial oversight and anomaly detection

### ✅ Prometheus Metrics
- **Feature**: Real-time metrics export
- **Implementation**: `enable_prometheus: true`
- **Security**: Monitoring for unusual patterns, alerting capability

### ✅ Health Endpoints
- **Feature**: Service health monitoring
- **Implementation**: `/health` endpoint with database checks
- **Security**: Early detection of service degradation

### ✅ Structured Logging
- **Feature**: JSON-formatted logs with correlation IDs
- **Implementation**: Configurable log levels
- **Security**: Easier log analysis and SIEM integration

### ✅ Connection Logging
- **Feature**: PostgreSQL connection tracking
- **Implementation**: `log_connections: on`, `log_disconnections: on`
- **Security**: Detect unauthorized access attempts

---

## 8. Privacy & Data Protection

### ✅ Telemetry Disabled
- **Feature**: No data sent to LiteLLM servers
- **Implementation**: `LITELLM_TELEMETRY: False`
- **Privacy**: Complete data sovereignty

### ✅ Message Redaction
- **Feature**: PII protection in logs and exceptions
- **Implementation**: 
  - `redact_messages_in_exceptions: true`
  - `redact_user_api_key_info: true`
- **Privacy**: Prevents sensitive data leakage in error messages

### ✅ API Key Dropping from Logs
- **Feature**: Remove API keys from debug logs
- **Implementation**: `drop_params: true`
- **Privacy**: Prevents key exposure in logs

### ✅ No Callbacks by Default
- **Feature**: Disable external data sharing
- **Implementation**: `success_callback: []`, `failure_callback: []`
- **Privacy**: Data stays within your infrastructure

### ✅ Local Data Storage
- **Feature**: All data stored locally in Docker volumes
- **Implementation**: Named volumes for PostgreSQL and Redis
- **Privacy**: No third-party storage dependencies

---

## 9. Secure Configuration

### ✅ Environment Variable Secrets
- **Feature**: All secrets loaded from environment
- **Implementation**: `os.environ/VAR_NAME` syntax
- **Security**: No hardcoded secrets in configuration files

### ✅ Read-Only Configuration Mount
- **Feature**: Config file mounted as read-only
- **Implementation**: `:ro` flag on volume mount
- **Security**: Prevents runtime config tampering

### ✅ Secure Defaults
- **Feature**: Security-first default settings
- **Implementation**: All security features enabled by default
- **Security**: Secure by default, opt-out rather than opt-in

### ✅ Configuration Validation
- **Feature**: Proxy validates config on startup
- **Implementation**: Detailed debug mode shows loaded config
- **Security**: Catches misconfigurations early

### ✅ Minimal Image
- **Feature**: Alpine-based images for minimal attack surface
- **Implementation**: `postgres:16-alpine`, `redis:7-alpine`
- **Security**: Fewer packages = fewer vulnerabilities

---

## 10. Vulnerability Management

### ✅ Regular Image Updates
- **Feature**: Use latest stable images
- **Implementation**: Version-pinned with update path
- **Security**: Timely security patches

### ✅ CVE Scanning
- **Feature**: Scan images for known vulnerabilities
- **Recommendation**: Use `docker scout cves` or similar tools
- **Security**: Proactive vulnerability detection

### ✅ Dependency Management
- **Feature**: Track and update dependencies
- **Implementation**: Use official images from trusted sources
- **Security**: Reduce supply chain risks

### ✅ Automated Security Updates
- **Feature**: Containers can be updated without data loss
- **Implementation**: Persistent volumes separate from containers
- **Security**: Easy to apply security patches

---

## Security Checklist

Use this checklist when deploying to production:

### Initial Setup
- [ ] Generated strong `LITELLM_MASTER_KEY` (32+ characters)
- [ ] Generated unique `LITELLM_SALT_KEY` (32+ characters)
- [ ] Set strong `POSTGRES_PASSWORD` (32+ characters)
- [ ] Set strong `REDIS_PASSWORD` (32+ characters)
- [ ] Reviewed and configured `ALLOWED_ORIGINS`
- [ ] Added `.env` to `.gitignore`
- [ ] Never committed `.env` to version control

### Network Security
- [ ] Configured firewall rules on host
- [ ] Set up reverse proxy (nginx/Caddy) with SSL
- [ ] Obtained SSL certificate (Let's Encrypt)
- [ ] Configured IP whitelisting (if needed)
- [ ] Disabled unnecessary ports

### Access Control
- [ ] Created separate keys for each client/application
- [ ] Set appropriate rate limits per key
- [ ] Set budget limits per key/team
- [ ] Tested key revocation process
- [ ] Documented key rotation procedure

### Monitoring
- [ ] Set up log aggregation
- [ ] Configured Prometheus scraping
- [ ] Set up alerting for anomalies
- [ ] Tested health check endpoints
- [ ] Configured backup monitoring

### Maintenance
- [ ] Scheduled regular database backups
- [ ] Documented backup restoration process
- [ ] Set up automated Docker image updates
- [ ] Configured log rotation
- [ ] Scheduled security review cadence

### Compliance
- [ ] Reviewed data residency requirements
- [ ] Documented data flow and storage
- [ ] Implemented data retention policies
- [ ] Configured audit log retention
- [ ] Prepared incident response plan

---

## Security Best Practices

### 1. Key Management
```bash
# Generate secure master key
openssl rand -hex 32 | awk '{print "sk-"$1}'

# Generate secure salt key
openssl rand -base64 32
```

### 2. Regular Backups
```bash
# Automated backup script
#!/bin/bash
docker compose exec postgres pg_dump -U litellm_user litellm | \
  gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### 3. Log Monitoring
```bash
# Monitor for suspicious activity
docker compose logs -f litellm | grep -i "error\|warning\|unauthorized"
```

### 4. Regular Updates
```bash
# Update all images
docker compose pull
docker compose up -d
```

### 5. Security Scanning
```bash
# Scan for vulnerabilities (if Docker Scout is available)
docker scout cves ghcr.io/berriai/litellm:main-latest
```

---

## Threat Model

### Protected Against

✅ **Unauthorized API Access** - Master key + virtual keys
✅ **API Key Theft** - Encrypted storage with salt key
✅ **Rate Limit Abuse** - Multiple rate limiting layers
✅ **Budget Exhaustion** - Per-key spending limits
✅ **Data Exfiltration** - Network isolation, no telemetry
✅ **Container Escape** - Non-root users, capability dropping
✅ **Man-in-the-Middle** - SSL/TLS verification
✅ **Privilege Escalation** - No-new-privileges flag
✅ **DoS Attacks** - Rate limits, resource constraints
✅ **SQL Injection** - Parameterized queries (LiteLLM SDK)
✅ **XSS Attacks** - Security headers
✅ **Clickjacking** - X-Frame-Options header

### Additional Considerations

⚠️ **Physical Access** - Ensure host machine security
⚠️ **Social Engineering** - Train team on key security
⚠️ **Supply Chain** - Monitor upstream image vulnerabilities
⚠️ **Zero-Day Exploits** - Keep systems updated, monitor security advisories

---

## Compliance Considerations

This setup helps with compliance for:

- **GDPR** - Data encryption, audit logs, data residency
- **HIPAA** - Encryption at rest/transit, audit trails, access controls
- **SOC 2** - Security controls, monitoring, logging
- **ISO 27001** - Information security management practices
- **PCI DSS** - (If processing payments) Encryption, access control, logging

⚠️ **Note**: This configuration provides security controls but does not guarantee compliance. Consult with compliance experts for your specific requirements.

---

## Incident Response

### If Master Key is Compromised

1. **Immediate Actions**:
   ```bash
   # Stop the proxy
   docker compose stop litellm
   
   # Generate new master key
   export NEW_MASTER_KEY=$(openssl rand -hex 32 | awk '{print "sk-"$1}')
   
   # Update .env file
   sed -i '' "s/LITELLM_MASTER_KEY=.*/LITELLM_MASTER_KEY=$NEW_MASTER_KEY/" .env
   
   # Restart proxy
   docker compose up -d litellm
   ```

2. **Revoke all virtual keys**
3. **Review audit logs for unauthorized access**
4. **Notify affected parties if data was accessed**

### If Virtual Key is Compromised

1. **Revoke the key immediately**:
   ```bash
   curl -X POST 'http://localhost:4000/key/delete' \
     -H 'Authorization: Bearer YOUR_MASTER_KEY' \
     -H 'Content-Type: application/json' \
     -d '{"key": "COMPROMISED_KEY"}'
   ```

2. **Review usage logs for that key**
3. **Generate new key for legitimate user**

### If Database is Compromised

1. **Immediately stop all services**
2. **Assess data exposure** (API keys are encrypted)
3. **Restore from backup if integrity is questioned**
4. **Rotate all credentials**
5. **Review access logs**

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [LiteLLM Security Documentation](https://docs.litellm.ai/docs/proxy/security)

---

## Summary

This setup implements **50+ security features** across 10 categories:

1. ✅ 4 Authentication & Authorization features
2. ✅ 4 Data Encryption features
3. ✅ 6 Network Security features
4. ✅ 6 Container Security features
5. ✅ 6 Database Security features
6. ✅ 7 Rate Limiting & Abuse Prevention features
7. ✅ 6 Audit Logging & Monitoring features
8. ✅ 5 Privacy & Data Protection features
9. ✅ 5 Secure Configuration features
10. ✅ 4 Vulnerability Management features

**Total: 53 security features implemented for maximal data safety.**
