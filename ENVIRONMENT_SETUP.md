# 🔐 Environment Variables Required for 24/7 Espionage Monitoring

## **Required Environment Variables**

### **🚨 CRITICAL - System Won't Start Without These**

#### 1. **DISCORD_TOKEN** ⭐
```bash
DISCORD_TOKEN=your_discord_bot_token_here
```
- **What it is**: Discord Bot Token from Discord Developer Portal
- **Used by**: Discord bot connection and commands
- **Where to get**: 
  1. Go to https://discord.com/developers/applications
  2. Create new application → Bot → Copy token
- **Example**: `DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4.GhIJKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz`

#### 2. **PNW_API_KEY** ⭐
```bash
PNW_API_KEY=your_politics_and_war_api_key
```
- **What it is**: Politics & War API Key for game data access
- **Used by**: All game data queries, nation monitoring, espionage checks
- **Where to get**:
  1. Log into Politics & War game
  2. Go to Account Settings → API Key
  3. Generate new key if needed
- **Example**: `PNW_API_KEY=05e5e3753de6b6f257f4abcd1234567890`

---

## **Optional Environment Variables** 

### **🌐 Web Dashboard Configuration**

#### 3. **FLASK_SECRET_KEY** (Recommended)
```bash
FLASK_SECRET_KEY=your_secret_key_for_web_sessions
```
- **What it is**: Secret key for Flask web dashboard sessions
- **Used by**: Web dashboard security, session management
- **Default**: `dev-secret-key` (not secure for production)
- **Generate**: Use any random string, preferably 32+ characters
- **Example**: `FLASK_SECRET_KEY=super_secret_random_string_12345`

#### 4. **WEB_HOST** (Optional)
```bash
WEB_HOST=0.0.0.0
```
- **What it is**: Host address for web dashboard
- **Used by**: Flask web server binding
- **Default**: `0.0.0.0` (listens on all interfaces)
- **Local only**: `127.0.0.1` or `localhost`

#### 5. **WEB_PORT** (Optional)
```bash
WEB_PORT=5000
```
- **What it is**: Port number for web dashboard
- **Used by**: Flask web server
- **Default**: `5000`
- **Alternative ports**: `3000`, `8080`, `8000`, etc.

#### 6. **DEBUG** (Optional)
```bash
DEBUG=True
```
- **What it is**: Enable debug mode for development
- **Used by**: Flask debug mode, extra logging
- **Default**: `True`
- **Production**: Set to `False`

---

## **📁 How to Set Up Environment Variables**

### **Method 1: .env File (Recommended)**

Create a file named `.env` in the project root:

```bash
# Politics & War 24/7 Espionage Monitoring Bot
# Copy this template and fill in your actual values

# 🚨 REQUIRED - System won't start without these
DISCORD_TOKEN=your_discord_bot_token_here
PNW_API_KEY=your_politics_and_war_api_key

# 🌐 Web Dashboard (Optional but recommended)
FLASK_SECRET_KEY=your_secret_key_here
WEB_HOST=0.0.0.0
WEB_PORT=5000

# 🐛 Development (Optional)
DEBUG=True
```

### **Method 2: System Environment Variables**

**Windows (Command Prompt)**:
```cmd
set DISCORD_TOKEN=your_token_here
set PNW_API_KEY=your_api_key_here
python main.py
```

**Windows (PowerShell)**:
```powershell
$env:DISCORD_TOKEN="your_token_here"
$env:PNW_API_KEY="your_api_key_here"
python main.py
```

**Linux/Mac (Bash)**:
```bash
export DISCORD_TOKEN="your_token_here"
export PNW_API_KEY="your_api_key_here"
python main.py
```

### **Method 3: Railway Deployment**

In Railway dashboard:
1. Go to your project
2. Click "Variables" tab
3. Add each variable:
   - `DISCORD_TOKEN` = your token
   - `PNW_API_KEY` = your key
   - `FLASK_SECRET_KEY` = random string

---

## **🔍 How to Get Required Tokens**

### **Getting Discord Bot Token**

1. **Go to Discord Developer Portal**:
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**:
   - Click "New Application"
   - Name it: "PnW Espionage Monitor" (or whatever you like)
   - Click "Create"

3. **Create Bot**:
   - Go to "Bot" section in left sidebar
   - Click "Add Bot"
   - Click "Yes, do it!"

4. **Get Token**:
   - Under "Token" section
   - Click "Copy" to copy your bot token
   - This is your `DISCORD_TOKEN`

5. **Set Permissions**:
   - Go to "OAuth2" → "URL Generator"
   - Scopes: Check "bot"
   - Bot Permissions: 
     - Send Messages
     - Embed Links
     - Read Message History
   - Copy generated URL and invite bot to your server

### **Getting Politics & War API Key**

1. **Log into Politics & War**:
   - Go to: https://politicsandwar.com/
   - Log into your account

2. **Access Account Settings**:
   - Click your nation name (top right)
   - Go to "Account" → "API Key"

3. **Generate API Key**:
   - If you don't have one, click "Generate New Key"
   - Copy the generated key
   - This is your `PNW_API_KEY`

4. **API Rate Limits**:
   - Standard: 120 requests per minute
   - The system respects these limits automatically

---

## **✅ Verification**

### **Check Your Setup**

Run this command to verify your environment variables:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['DISCORD_TOKEN', 'PNW_API_KEY']
optional = ['FLASK_SECRET_KEY', 'WEB_HOST', 'WEB_PORT', 'DEBUG']

print('🔍 Environment Variable Check')
print('=' * 40)

for var in required:
    value = os.getenv(var)
    if value:
        print(f'✅ {var}: Set (length: {len(value)})')
    else:
        print(f'❌ {var}: MISSING (REQUIRED)')

print()
for var in optional:
    value = os.getenv(var)
    if value:
        print(f'ℹ️  {var}: {value}')
    else:
        print(f'⚪ {var}: Using default')
"
```

### **Test the System**

```bash
# Test if environment variables work
python test_24_7_system.py

# Run the full system
python main.py
```

---

## **🚨 Security Notes**

### **Keep Tokens Secret**
- ❌ **Never commit** `.env` file to git
- ❌ **Never share** your Discord token or API key
- ❌ **Never post** tokens in screenshots or forums
- ✅ **Use** `.env` file for local development
- ✅ **Use** platform environment variables for production

### **Token Safety**
- **Discord Token**: Can control your bot completely
- **PNW API Key**: Can access your nation's data
- **If compromised**: Regenerate immediately

### **.gitignore Protection**
The `.env` file is already ignored by git:
```gitignore
# Environment variables
.env
```

---

## **🎯 Minimal Working Setup**

For the 24/7 monitoring system to work, you only need:

```bash
# .env file - minimum required
DISCORD_TOKEN=your_discord_bot_token_here
PNW_API_KEY=your_politics_and_war_api_key
```

Everything else will use sensible defaults:
- Web dashboard: http://localhost:5000
- Debug mode: Enabled
- Database: `spy_bot.db` in project folder
- 24/7 monitoring: Auto-starts when bot connects

That's it! The system will automatically start monitoring alliance nations and detecting daily reset times. 🚀
