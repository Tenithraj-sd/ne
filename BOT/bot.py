import asyncio
import nest_asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Allow nested asyncio loops
nest_asyncio.apply()

# Replace with your user ID and bot token
from config import MY_USER_ID,BOT_TOKEN
# Utility Functions
async def send_response(update: Update, message: str):
    """Send a text response to the user."""
    await update.message.reply_text(message)


def is_authorized(update: Update) -> bool:
    """Check if the user is authorized."""
    return update.message.from_user.id == MY_USER_ID


async def handle_unauthorized(update: Update):
    """Handle unauthorized access."""
    await send_response(update, "Bye bye!")
    # Optionally delete the user's message (requires admin permissions in group chats)
    await update.message.delete()


# Command Handlers
async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the list of available commands."""
    if not is_authorized(update):
        await handle_unauthorized(update)
        return

    commands = [
        BotCommand("help", "Show the list of available commands."),
        BotCommand("screenshot", "Take a screenshot of your screen."),
        BotCommand("system_usage", "Get system usage information."),
        BotCommand("battery_percentage"," send_battery_percentage"),
        BotCommand("power_off","To Turn OFF SYSTEM"),
        BotCommand("reboot_system","to REBOOT The SYSTEM"),

    ]

    try:
        message = "Available commands:\n\n"
        for command in commands:
            message += f"/{command.command} - {command.description}\n"
        await update.message.reply_text(message)
    except Exception as e:
        await send_response(update, f"Error: {e}")


async def system_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system usage information."""
    if not is_authorized(update):
        await handle_unauthorized(update)
        return

    import shutil
    import psutil

    try:
        # Get memory stats
        memory = psutil.virtual_memory()
        total_ram = round(memory.total / (1024 ** 3), 2)  # Convert to GB
        used_ram = round(memory.used / (1024 ** 3), 2)    # Convert to GB
        free_ram = round(memory.available / (1024 ** 3), 2)  # Convert to GB

        memory_info = f"RAM Usage:\nTotal: {total_ram} GB\nUsed: {used_ram} GB\nFree: {free_ram} GB\n"

        # Disk stats for '/' and '/home'
        disk_info = "Disk Usage:\n"
        for mountpoint in ['/', '/home']:
            try:
                usage = shutil.disk_usage(mountpoint)
                total_disk = round(usage.total / (1024 ** 3), 2)  # Convert to GB
                used_disk = round(usage.used / (1024 ** 3), 2)    # Convert to GB
                free_disk = round(usage.free / (1024 ** 3), 2)    # Convert to GB
                disk_info += (
                    f"Partition: {mountpoint}\n"
                    f"  Total: {total_disk} GB\n"
                    f"  Used: {used_disk} GB\n"
                    f"  Free: {free_disk} GB\n"
                )
            except FileNotFoundError:
                disk_info += f"Partition: {mountpoint}\n  Not Found\n"

        # Combine and send the message
        system_info = f"{memory_info}\n{disk_info}"
        await send_response(update, system_info)

    except Exception as e:
        await send_response(update, f"Error: {e}")

import psutil,os

async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Take a screenshot and send it to the user."""
    if not is_authorized(update):
        await handle_unauthorized(update)
        return

    import pyautogui
    from io import BytesIO

    try:
        screenshot = pyautogui.screenshot()
        img_byte_array = BytesIO()
        screenshot.save(img_byte_array, format="PNG")
        img_byte_array.seek(0)
        await update.message.reply_photo(photo=img_byte_array)
    except Exception as e:
        await send_response(update, f"Error: {e}")

async def send_battery_percentage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MY_USER_ID = context.bot_data.get('MY_USER_ID')
    if not is_authorized(update, MY_USER_ID):
        await handle_unauthorized(update)
        return

    try:
        battery = psutil.sensors_battery()
        battery_percentage = battery.percent if battery else None
        await send_response(update, f"Battery level: {battery_percentage}%") if battery_percentage else await send_response(update, "Could not retrieve battery info.")
    except Exception as e:
        await send_response(update, f"Error: {e}")

async def power_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MY_USER_ID = context.bot_data.get('MY_USER_ID')
    if not is_authorized(update, MY_USER_ID):
        await handle_unauthorized(update)
        return

    try:
        os.system("poweroff")
        # Run the poweroff command
        # subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)
        await send_response(update, "System is shutting down...")
    except Exception as e:
        await send_response(update, f"Error: {e}")

# Function to reboot the system
async def reboot_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MY_USER_ID = context.bot_data.get('MY_USER_ID')
    if not is_authorized(update, MY_USER_ID):
        await handle_unauthorized(update)
        return

    try:
        # Run the reboot command
        os.system("reboot")
        # subprocess.run(['sudo', 'reboot'], check=True)
        await send_response(update, "System is rebooting...")
    except Exception as e:
        await send_response(update, f"Error: {e}")

async def set_bot_commands(application):
    """Set bot commands."""
    commands = [
        BotCommand("help", "Show the list of available commands."),
        BotCommand("screenshot", "Take a screenshot of your screen."),
        BotCommand("system_usage", "Get system usage information."),
        BotCommand("battery_percentage"," send_battery_percentage"),
        BotCommand("power_off","To Turn OFF SYSTEM"),
        BotCommand("reboot_system","to REBOOT The SYSTEM"),
    ]
    await application.bot.set_my_commands(commands)


def start_bot():
    """Start the Telegram bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("help", show_commands))
    application.add_handler(CommandHandler("screenshot", take_screenshot))
    application.add_handler(CommandHandler("system_usage", system_usage))
    application.add_handler(CommandHandler("start", show_commands))
    application.add_handler(CommandHandler("battery_percentage", send_battery_percentage))
    application.add_handler(CommandHandler("power_off", power_off))
    application.add_handler(CommandHandler("reboot_system",reboot_system ))
    async def run():
        await set_bot_commands(application)
        print("Bot is running...")
        await application.run_polling()

    # Handle running event loop
    try:
        asyncio.get_running_loop().run_until_complete(run())
    except RuntimeError:  # If no event loop is running
        asyncio.run(run())


if __name__ == "__main__":
    start_bot()
