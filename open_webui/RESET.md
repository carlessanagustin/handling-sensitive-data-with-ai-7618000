Here’s a clean, short **README** you can drop into your project:

---

# Resetting Admin Access for OpenWebUI (Docker)

This guide explains how to reset the admin password for OpenWebUI without deleting models or wiping the entire volume.

## 1. Enter the OpenWebUI container

```bash
docker compose exec openwebui bash
```

## 2. Install required tools (one-time)

```bash
apt-get update
apt-get install -y apache2-utils sqlite3
```

## 3. Generate a new bcrypt password hash

Replace `NEWPASSWORD` with your new password:

```bash
NEWPASS='NEWPASSWORD'
HASH=$(htpasswd -bnBC 10 "" "$NEWPASS" | cut -d: -f2 | tr -d '\n')
echo "$HASH"
```

## 4. Update the password in the `auth` table

Replace the email with your OpenWebUI account email:

```bash
sqlite3 /app/backend/data/webui.db \
  "UPDATE auth SET password='$HASH', active=1 WHERE email='your@email.com';"
```

## 5. Ensure the user is an admin

```bash
sqlite3 /app/backend/data/webui.db \
  "UPDATE user SET role='admin' WHERE email='your@email.com';"
```

## 6. Restart OpenWebUI

On the host machine:

```bash
docker compose restart openwebui
```

## 7. Log in

Use your email and the new password you set.

---

If you want, I can also produce a more polished or longer version (with troubleshooting, screenshots, or markdown formatting for GitHub).

