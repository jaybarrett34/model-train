# AOTR Discord Webhook Bot

A Discord bot that listens for webhook events from your AOTR (Anime Online Tower Rush) script and pings you when you gain serum or mythic items.

## Features

- 🎯 Listens for webhook POST requests from your AOTR script
- 💉 Notifies you when you gain serum
- ✨ Notifies you when you gain mythic items
- 🔔 Pings you directly in Discord
- 🎨 Beautiful embed messages with different colors for different item types
- 🔒 Optional webhook secret for security
- 📊 Status commands to check bot health
- 🧪 Test endpoint to verify functionality

## Prerequisites

- Python 3.8 or higher
- A Discord bot token (see setup instructions below)
- A Discord server where you have permission to add bots

## Setup Instructions

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "AOTR Notifier")
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot" and confirm
5. Under "TOKEN", click "Reset Token" and copy it (you'll need this later)
6. Under "Privileged Gateway Intents", enable:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT (optional)

### 2. Invite the Bot to Your Server

1. In the Developer Portal, go to "OAuth2" → "URL Generator"
2. Select the following scopes:
   - `bot`
   - `applications.commands`
3. Select the following bot permissions:
   - Send Messages
   - Embed Links
   - Mention Everyone (if you want to be pinged)
   - Read Message History
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 3. Get Your Discord IDs

**Channel ID:**
1. In Discord, go to User Settings → Advanced → Enable "Developer Mode"
2. Right-click the channel where you want notifications → Copy ID

**User ID (for pinging):**
1. Right-click your username in Discord → Copy ID

### 4. Install Dependencies

```bash
cd /path/to/model-train
pip install -r requirements-discord-bot.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project directory (or add to existing `.env`):

```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
DISCORD_USER_ID=your_user_id_here

# Webhook Configuration
WEBHOOK_PORT=5555
WEBHOOK_SECRET=your_secret_key_here  # Optional but recommended
```

**Example `.env`:**
```bash
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_FROM_DISCORD_DEVELOPER_PORTAL
DISCORD_CHANNEL_ID=1234567890123456789
DISCORD_USER_ID=9876543210987654321
WEBHOOK_PORT=5555
WEBHOOK_SECRET=my_super_secret_key_123
```

### 6. Run the Bot

```bash
python discord_aotr_bot.py
```

You should see output like:
```
2024-01-01 12:00:00 - __main__ - INFO - 🚀 Starting AOTR Discord Webhook Bot...
2024-01-01 12:00:00 - __main__ - INFO - 📡 Webhook server will listen on http://0.0.0.0:5555/webhook
2024-01-01 12:00:00 - __main__ - INFO - ✅ Webhook server thread started
2024-01-01 12:00:00 - __main__ - INFO - 🔌 Connecting to Discord...
2024-01-01 12:00:01 - __main__ - INFO - ✅ Discord bot logged in as AOTR Notifier (ID: 1234567890)
2024-01-01 12:00:01 - __main__ - INFO - 📡 Webhook server listening on port 5555
```

## Usage

### Testing the Bot

#### Test via Discord Commands

In your Discord channel, type:
```
!ping     # Check if bot is responsive
!status   # View bot configuration and status
```

#### Test via Webhook

Send a test webhook using curl:

```bash
curl -X POST http://localhost:5555/test
```

Or send a custom webhook:

```bash
curl -X POST http://localhost:5555/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "mythic",
    "item_name": "Divine Dragon Serum",
    "quantity": 1,
    "secret": "your_secret_key_here",
    "extra": {
      "rarity": "Legendary",
      "location": "Elite Zone"
    }
  }'
```

### Integrating with Your AOTR Script

From your AOTR script (or any script), send a POST request to the webhook:

#### Python Example

```python
import requests

def notify_discord(item_type, item_name, quantity=1, **extra):
    webhook_url = "http://localhost:5555/webhook"

    payload = {
        "type": item_type,  # "serum" or "mythic"
        "item_name": item_name,
        "quantity": quantity,
        "secret": "your_secret_key_here",
        "extra": extra
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print(f"✅ Notification sent: {item_name}")
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Example usage
notify_discord("mythic", "Shadow Blade", 1, rarity="Legendary", zone="Dark Forest")
notify_discord("serum", "Speed Serum", 3)
```

#### JavaScript/Node.js Example

```javascript
async function notifyDiscord(itemType, itemName, quantity = 1, extra = {}) {
    const webhookUrl = "http://localhost:5555/webhook";

    const payload = {
        type: itemType,  // "serum" or "mythic"
        item_name: itemName,
        quantity: quantity,
        secret: "your_secret_key_here",
        extra: extra
    };

    try {
        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            console.log(`✅ Notification sent: ${itemName}`);
        } else {
            console.log(`❌ Failed to send notification: ${response.status}`);
        }
    } catch (error) {
        console.error(`❌ Error: ${error}`);
    }
}

// Example usage
notifyDiscord("mythic", "Lightning Staff", 1, { rarity: "Epic", zone: "Thunder Peak" });
notifyDiscord("serum", "Health Serum", 5);
```

#### Lua/Roblox Example

```lua
local HttpService = game:GetService("HttpService")

function notifyDiscord(itemType, itemName, quantity, extra)
    local webhookUrl = "http://localhost:5555/webhook"

    local payload = {
        type = itemType,  -- "serum" or "mythic"
        item_name = itemName,
        quantity = quantity or 1,
        secret = "your_secret_key_here",
        extra = extra or {}
    }

    local success, response = pcall(function()
        return HttpService:PostAsync(
            webhookUrl,
            HttpService:JSONEncode(payload),
            Enum.HttpContentType.ApplicationJson
        )
    end)

    if success then
        print("✅ Notification sent: " .. itemName)
    else
        warn("❌ Failed to send notification: " .. tostring(response))
    end
end

-- Example usage
notifyDiscord("mythic", "Dragon Blade", 1, { rarity = "Legendary", zone = "Dragon's Lair" })
notifyDiscord("serum", "Speed Boost", 3)
```

## Webhook API Reference

### Endpoint

```
POST http://your-server:5555/webhook
```

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Type of item: "serum", "mythic", or "item" |
| `item_name` | string | Yes | Name of the item obtained |
| `quantity` | integer | No | Quantity obtained (default: 1) |
| `secret` | string | Conditional | Required if WEBHOOK_SECRET is set |
| `extra` | object | No | Additional data to display (e.g., rarity, location) |

### Example Request

```json
{
    "type": "mythic",
    "item_name": "Celestial Sword",
    "quantity": 1,
    "secret": "your_secret_key_here",
    "extra": {
        "rarity": "Legendary",
        "location": "Heaven's Gate",
        "level": 50
    }
}
```

### Response

**Success (200):**
```json
{
    "success": true,
    "message": "Notification sent",
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Error (400):**
```json
{
    "error": "No JSON data provided"
}
```

**Error (403):**
```json
{
    "error": "Invalid secret"
}
```

## Troubleshooting

### Bot doesn't connect to Discord

- ✅ Check that `DISCORD_BOT_TOKEN` is correct in your `.env` file
- ✅ Ensure your bot has the required intents enabled in the Developer Portal
- ✅ Verify your internet connection

### Webhook not working

- ✅ Check that the Flask server is running (you should see logs)
- ✅ Verify the webhook URL is correct (`http://localhost:5555/webhook`)
- ✅ If using a `WEBHOOK_SECRET`, ensure it matches in both the bot and your script
- ✅ Check firewall settings if accessing from another machine

### Not getting pinged

- ✅ Verify `DISCORD_USER_ID` is set correctly in `.env`
- ✅ Ensure the bot has permission to mention users in the channel
- ✅ Check that notifications are enabled for that channel in your Discord settings

### Bot crashes or stops

- ✅ Check the logs for error messages
- ✅ Ensure all dependencies are installed: `pip install -r requirements-discord-bot.txt`
- ✅ Verify Python version is 3.8 or higher: `python --version`

## Running as a Service (Linux)

To keep the bot running 24/7, you can create a systemd service:

1. Create a service file:
```bash
sudo nano /etc/systemd/system/aotr-discord-bot.service
```

2. Add the following content:
```ini
[Unit]
Description=AOTR Discord Webhook Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/model-train
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/model-train/discord_aotr_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable aotr-discord-bot
sudo systemctl start aotr-discord-bot
sudo systemctl status aotr-discord-bot
```

4. View logs:
```bash
sudo journalctl -u aotr-discord-bot -f
```

## Security Considerations

- 🔒 Always use a `WEBHOOK_SECRET` to prevent unauthorized notifications
- 🔒 Don't commit your `.env` file to version control
- 🔒 If exposing the webhook to the internet, use HTTPS (consider nginx reverse proxy)
- 🔒 Keep your Discord bot token private

## License

MIT License - Feel free to modify and use as needed!

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all configuration in `.env` is correct
3. Test with the `/test` endpoint first
4. Ensure Discord bot permissions are correct

Happy gaming! 🎮✨
