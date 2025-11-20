#!/usr/bin/env python3
"""
Discord AOTR Webhook Bot
Listens for webhook events from AOTR script and pings you when you gain serum/mythic items.
"""

import os
import asyncio
import logging
from datetime import datetime
from threading import Thread
from typing import Optional

import discord
from discord.ext import commands
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
DISCORD_USER_ID = int(os.getenv("DISCORD_USER_ID", "0"))  # Your Discord user ID for pinging
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "5555"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # Optional secret for authentication

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask Webhook Server Setup
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Store bot reference for Flask to use
discord_bot = None


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord."""
    logger.info(f"✅ Discord bot logged in as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"📡 Webhook server listening on port {WEBHOOK_PORT}")

    if DISCORD_CHANNEL_ID:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            logger.info(f"📢 Notification channel set: #{channel.name}")
        else:
            logger.warning(f"⚠️  Could not find channel with ID {DISCORD_CHANNEL_ID}")


@bot.command(name="ping")
async def ping_command(ctx):
    """Test command to check if bot is responsive."""
    await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")


@bot.command(name="status")
async def status_command(ctx):
    """Check bot status and configuration."""
    status_msg = f"""
**AOTR Bot Status** 🤖

✅ Bot is online and running
📡 Webhook listening on port: {WEBHOOK_PORT}
📢 Notification channel: <#{DISCORD_CHANNEL_ID}>
🔔 Ping user: <@{DISCORD_USER_ID}>
⏰ Uptime: {datetime.now()}
    """
    await ctx.send(status_msg)


async def send_notification(message_type: str, item_name: str, quantity: int = 1, extra_data: dict = None):
    """
    Send a notification to the configured Discord channel.

    Args:
        message_type: Type of notification (serum, mythic, etc.)
        item_name: Name of the item gained
        quantity: Quantity gained (default: 1)
        extra_data: Additional data to include in the notification
    """
    try:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            logger.error(f"Could not find channel with ID {DISCORD_CHANNEL_ID}")
            return

        # Build the notification message
        ping = f"<@{DISCORD_USER_ID}>" if DISCORD_USER_ID else ""

        # Create an embed for better formatting
        embed = discord.Embed(
            title="🎉 AOTR Notification",
            color=discord.Color.gold() if message_type == "mythic" else discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        # Set emoji and title based on type
        if message_type.lower() == "mythic":
            embed.add_field(name="✨ Mythic Obtained!", value=f"**{item_name}**", inline=False)
        elif message_type.lower() == "serum":
            embed.add_field(name="💉 Serum Gained!", value=f"**{item_name}**", inline=False)
        else:
            embed.add_field(name="🎁 Item Obtained!", value=f"**{item_name}**", inline=False)

        # Add quantity if specified
        if quantity > 1:
            embed.add_field(name="Quantity", value=str(quantity), inline=True)

        # Add extra data if provided
        if extra_data:
            for key, value in extra_data.items():
                embed.add_field(name=key.replace("_", " ").title(), value=str(value), inline=True)

        # Send the message
        await channel.send(content=ping, embed=embed)
        logger.info(f"✅ Sent {message_type} notification: {item_name} (x{quantity})")

    except Exception as e:
        logger.error(f"❌ Error sending notification: {e}", exc_info=True)


# Flask Webhook Routes

@app.route("/")
def home():
    """Health check endpoint."""
    return jsonify({
        "status": "online",
        "service": "AOTR Discord Webhook Bot",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Main webhook endpoint for receiving AOTR events.

    Expected JSON format:
    {
        "type": "serum" | "mythic" | "item",
        "item_name": "Item Name",
        "quantity": 1,
        "secret": "your_webhook_secret",  // Optional
        "extra": {  // Optional additional data
            "rarity": "legendary",
            "location": "Zone 5"
        }
    }
    """
    try:
        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate secret if configured
        if WEBHOOK_SECRET and data.get("secret") != WEBHOOK_SECRET:
            logger.warning("⚠️  Webhook request with invalid secret")
            return jsonify({"error": "Invalid secret"}), 403

        # Extract data
        message_type = data.get("type", "item")
        item_name = data.get("item_name", "Unknown Item")
        quantity = data.get("quantity", 1)
        extra_data = data.get("extra", {})

        # Log the event
        logger.info(f"📥 Webhook received: {message_type} - {item_name} (x{quantity})")

        # Send notification asynchronously
        asyncio.run_coroutine_threadsafe(
            send_notification(message_type, item_name, quantity, extra_data),
            bot.loop
        )

        return jsonify({
            "success": True,
            "message": "Notification sent",
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/test", methods=["POST", "GET"])
def test_endpoint():
    """Test endpoint to manually trigger a notification."""
    try:
        asyncio.run_coroutine_threadsafe(
            send_notification("serum", "Test Serum", 1, {"location": "Test Zone"}),
            bot.loop
        )
        return jsonify({"success": True, "message": "Test notification sent"}), 200
    except Exception as e:
        logger.error(f"❌ Error sending test notification: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def run_flask():
    """Run Flask webhook server in a separate thread."""
    app.run(host="0.0.0.0", port=WEBHOOK_PORT, debug=False, use_reloader=False)


def main():
    """Main entry point - runs both Discord bot and Flask webhook server."""
    global discord_bot
    discord_bot = bot

    # Validate configuration
    if not DISCORD_TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN not set in environment variables!")
        return

    if not DISCORD_CHANNEL_ID:
        logger.error("❌ DISCORD_CHANNEL_ID not set in environment variables!")
        return

    logger.info("🚀 Starting AOTR Discord Webhook Bot...")
    logger.info(f"📡 Webhook server will listen on http://0.0.0.0:{WEBHOOK_PORT}/webhook")

    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Webhook server thread started")

    # Start Discord bot (this blocks)
    logger.info("🔌 Connecting to Discord...")
    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
