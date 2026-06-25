from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(
    title="Vercel + FastAPI",
    description="Vercel + FastAPI",
    version="1.0.0",

import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, Dict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatMemberStatus

# ================= CONFIGURATION =================
BOT_TOKEN = "8618375095:AAEh-zURJfh7kHmr1U7j22BYMz3LwaTIlqc"

# API Endpoints
API_ENDPOINTS = {
    "mobile": "https://api.b77bf911.workers.dev/mobile?number=",
    "vehicle": "https://api.b77bf911.workers.dev/vehicle?registration=",
    "aadhaar": "https://api.b77bf911.workers.dev/aadhaar?id=",
    "upi": "https://api.b77bf911.workers.dev/upi?id=",
    "pan": "https://api.b77bf911.workers.dev/pan?pan=",
}

ADMIN_ID = 7695907004
ALLOWED_GROUPS = [-1003108067359]

# Messages
MESSAGES = {
    "private_block": (
        "🚫 *Access Restricted*\n\n"
        "This bot is exclusively available in authorized groups.\n"
        "To gain access, join our official channels:\n\n"
        "📢 Main Channel: [@ShashiDevelopment](t.me/ShashiDevelopment)\n"
        "💬 Discussion: [@bshashi_secret](https://t.me/+e9sp9UFShgMwOGU1)\n\n"
        "⚠️ Unauthorized private usage is not permitted."
    ),
    "api_error": (
        "🔧 *Service Temporarily Unavailable*\n\n"
        "The lookup service is currently experiencing high load. "
        "Please try again in a few moments."
    ),
    "invalid_input": (
        "❌ *Invalid Input*\n\n"
        "Please check the format and try again.\n"
        "Use `/help` for command usage."
    ),
    "no_args": (
        "❌ *Missing Input*\n\n"
        "Please provide the required input.\n"
        "Example: `/num 9876543210`"
    ),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) Chrome/120",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

# ================= UTILITY FUNCTIONS =================
async def fetch_json(url: str, max_retries: int = 3) -> Optional[Dict]:
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
        for attempt in range(max_retries):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        await asyncio.sleep(1)
            except asyncio.TimeoutError:
                await asyncio.sleep(1)
            except Exception:
                await asyncio.sleep(1)
    
    return None

def format_response_time(start_time: datetime) -> str:
    elapsed = (datetime.now() - start_time).total_seconds()
    return f"{elapsed:.2f}s"

def validate_input(input_str: str, input_type: str) -> bool:
    if not input_str:
        return False
    
    input_str = input_str.strip()
    
    if input_type == "mobile":
        return len(input_str) == 10 and input_str.isdigit()
    elif input_type == "vehicle":
        return 8 <= len(input_str) <= 12
    elif input_type == "aadhaar":
        return len(input_str) == 12 and input_str.isdigit()
    elif input_type == "pan":
        return len(input_str) == 10
    elif input_type == "upi":
        return '@' in input_str and len(input_str) <= 50
    
    return True

def is_authorized_chat(chat_id: int) -> bool:
    return chat_id in ALLOWED_GROUPS

# ================= COMMAND HANDLERS =================
async def private_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MESSAGES["private_block"],
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # यहाँ फिक्स किया है - सिर्फ private chat check
    if update.effective_chat.type == "private" and update.effective_user.id != ADMIN_ID:
        await private_block(update, context)
        return
    
    help_text = (
        "🔍 *SECRET PLATFORM BOT*\n\n"
        "*Available Commands:*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 `/num <10-digit mobile>` - Mobile number lookup\n"
        "🚗 `/gaadi <vehicle number>` - Vehicle registration details\n"
        "🆔 `/adhar <12-digit Aadhaar>` - Aadhaar information\n"
        "💸 `/upi <VPA@bank>` - UPI verification\n"
        "🪪 `/pan <PAN number>` - PAN card details\n"
        "🆔 `/chatid` - Get group chat ID (Admins only)\n"
        "ℹ️ `/help` - Show this help message\n"
        "📊 `/stats` - Bot usage statistics (Admin only)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Usage Tips:*\n"
        "• All lookups require proper authorization\n"
        "• For support, contact @bshashi_secret\n\n"
        f"🕒 Last Updated: {datetime.now().strftime('%Y-%m-%d')}"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private" and update.effective_user.id != ADMIN_ID:
        await private_block(update, context)
        return
    
    welcome_text = (
        "🤖 *Welcome to Secret Platform Bot*\n\n"
        "I can help you lookup various information securely.\n\n"
        "Use `/help` to see all available commands.\n\n"
        "⚠️ *Note:* This bot works only in authorized groups."
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ This command is for administrators only.")
        return
    
    stats_text = (
        "📊 *Bot Statistics*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🔧 Admin ID: `{ADMIN_ID}`\n"
        f"👥 Allowed Groups: `{len(ALLOWED_GROUPS)}`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🕒 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")

class LookupHandler:
    
    @staticmethod
    async def _perform_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE, api_type: str, input_type: str, loading_message: str):
        start_time = datetime.now()
        
        # Check if in private chat (except admin)
        if update.effective_chat.type == "private" and update.effective_user.id != ADMIN_ID:
            await private_block(update, context)
            return
        
        # Check if in group and group is authorized
        if update.effective_chat.type in ["group", "supergroup"]:
            if not is_authorized_chat(update.effective_chat.id):
                await update.message.reply_text(
                    "❌ *Unauthorized Group*\n\nThis bot is not authorized in this group.",
                    parse_mode="Markdown"
                )
                return
        
        # Check if arguments are provided
        if not context.args:
            await update.message.reply_text(
                MESSAGES["no_args"],
                parse_mode="Markdown"
            )
            return
        
        query = context.args[0]
        
        # Validate input
        if not validate_input(query, input_type):
            await update.message.reply_text(
                MESSAGES["invalid_input"],
                parse_mode="Markdown"
            )
            return
        
        # Send loading message
        wait_msg = await update.message.reply_text(f"🔍 {loading_message}")
        
        # Fetch data
        api_url = API_ENDPOINTS[api_type] + query
        data = await fetch_json(api_url)
        
        if not data:
            await wait_msg.edit_text(
                f"❌ *Lookup Failed*\n\n{MESSAGES['api_error']}\n"
                f"Response time: {format_response_time(start_time)}",
                parse_mode="Markdown"
            )
            return
        
        # Check for success in response
        if not data.get("success", False):
            await wait_msg.edit_text(
                f"❌ *No Data Found*\n\nNo records found for `{query}`\n"
                f"Response time: {format_response_time(start_time)}",
                parse_mode="Markdown"
            )
            return
        
        # Process and format response
        formatted_response = await LookupHandler._format_response(
            api_type, data, query, format_response_time(start_time)
        )
        
        await wait_msg.edit_text(formatted_response, parse_mode="Markdown")
    
    @staticmethod
    async def _format_response(api_type: str, data: Dict, query: str, response_time: str) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if api_type == "mobile":
            return LookupHandler._format_mobile_response(data, query, timestamp, response_time)
        elif api_type == "vehicle":
            return LookupHandler._format_vehicle_response(data, query, timestamp, response_time)
        elif api_type == "aadhaar":
            return LookupHandler._format_aadhaar_response(data, query, timestamp, response_time)
        elif api_type == "upi":
            return LookupHandler._format_upi_response(data, query, timestamp, response_time)
        elif api_type == "pan":
            return LookupHandler._format_pan_response(data, query, timestamp, response_time)
        
        return "❌ *Error formatting response*"
    
    @staticmethod
    def _format_mobile_response(data: Dict, query: str, timestamp: str, response_time: str) -> str:
        result_data = data.get("data", {}).get("data", {}).get("result")
        
        if not result_data:
            return f"❌ *No records found for* `{query}`"
        
        # Handle both list and dict response
        if isinstance(result_data, list):
            if not result_data:
                return f"❌ *No records found for* `{query}`"
            result = result_data[0]
        elif isinstance(result_data, dict):
            if result_data.get("message"):
                return f"❌ *No records found for* `{query}`"
            result = result_data
        else:
            return f"❌ *Invalid response format for* `{query}`"
        
        return (
            "📱 *MOBILE NUMBER LOOKUP*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔢 *Number:* `{result.get('mobile', query)}`\n"
            f"👤 *Name:* `{result.get('name', 'N/A')}`\n"
            f"👨 *Father:* `{result.get('father_name', 'N/A')}`\n"
            f"📍 *Circle:* `{result.get('circle', 'N/A')}`\n"
            f"📞 *Alternate:* `{result.get('alt_mobile', 'N/A')}`\n"
            f"🆔 *ID Number:* `{result.get('id_number', 'N/A')}`\n"
            f"📧 *Email:* `{result.get('email', 'N/A')}`\n\n"
            f"🏠 *Address:*\n`{result.get('address', 'N/A')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Response: {response_time} | 📅 {timestamp}"
        )
    
    @staticmethod
def _format_vehicle_response(data: Dict, query: str, timestamp: str, response_time: str) -> str:
    address = data.get("address", {})
    challan_block = data.get("challan", {})

    if not address:
        return f"❌ *No vehicle found for* `{query}`"

    # Challan data
    challans = challan_block.get("data", [])
    if challans:
        challan_text = "\n".join(
            [
                f"• `{c.get('number', 'N/A')}` | ₹{c.get('amount', {}).get('total', '0')} | "
                f"{c.get('challan_status', 'N/A')}"
                for c in challans[:5]
            ]
        )
    else:
        challan_text = "• No challans found"

    return (
        "🚗 *VEHICLE REGISTRATION DETAILS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔖 *Registration No:* `{address.get('asset_number', query)}`\n"
        f"🛵 *Vehicle Type:* `{address.get('vehicle_type', 'N/A')}`\n"
        f"🏍 *Make & Model:* `{address.get('make_model', 'N/A')}`\n"
        f"🏭 *Manufacturer:* `{address.get('make_name', 'N/A')}`\n"
        f"🧾 *Model Name:* `{address.get('model_name', 'N/A')}`\n"
        f"⛽ *Fuel Type:* `{address.get('fuel_type', 'N/A')}`\n"
        f"📆 *Registration Date:* `{address.get('registration_date', 'N/A')}`\n"
        f"📅 *Reg Month/Year:* `{address.get('registration_month', 'N/A')}/"
        f"{address.get('registration_year', 'N/A')}`\n"
        f"🏢 *RTO Office:* `{address.get('registration_address', 'N/A')}`\n"
        f"🔧 *Engine No:* `{address.get('engine_number', 'N/A')}`\n"
        f"🧩 *Chassis No:* `{address.get('chassis_number', 'N/A')}`\n"
        f"👤 *Owner Name:* `{address.get('owner_name', 'N/A')}`\n"
        f"🚕 *Commercial:* `{address.get('is_commercial', False)}`\n"
        f"📄 *Policy Expired:* `{address.get('previous_policy_expired', False)}`\n"
        f"📆 *Policy Expiry:* `{address.get('previous_policy_expiry_date', 'N/A')}`\n\n"
        f"🏠 *Permanent Address:*\n`{address.get('permanent_address', 'N/A')}`\n\n"
        f"📍 *Present Address:*\n`{address.get('present_address', 'N/A')}`\n\n"
        "🚨 *Challan Information*\n"
        f"{challan_text}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Response Time: {response_time}\n"
        f"📅 Checked On: {timestamp}"
    )
    
    @staticmethod
    def _format_aadhaar_response(data: Dict, query: str, timestamp: str, response_time: str) -> str:
        result_data = data.get("data", {}).get("result")
        
        if not result_data:
            return f"❌ *No Aadhaar records found for* `{query}`"
        
        # Handle both list and dict response
        if isinstance(result_data, list):
            if not result_data:
                return f"❌ *No records found for* `{query}`"
            result = result_data[0]
        elif isinstance(result_data, dict):
            if result_data.get("message"):
                return f"❌ *No records found for* `{query}`"
            result = result_data
        else:
            return f"❌ *Invalid response format for* `{query}`"
        
        return (
            "🆔 *AADHAAR LOOKUP*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Name:* `{result.get('name', 'N/A')}`\n"
            f"👨 *Father's Name:* `{result.get('father_name', 'N/A')}`\n"
            f"🔢 *Aadhaar:* `{result.get('id_number', query)}`\n"
            f"📞 *Mobile:* `{result.get('mobile', 'N/A')}`\n"
            f"📧 *Email:* `{result.get('email', 'N/A')}`\n\n"
            f"🏠 *Address:*\n`{result.get('address', 'N/A')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Response: {response_time} | 📅 {timestamp}"
        )
    
    @staticmethod
    def _format_upi_response(data: Dict, query: str, timestamp: str, response_time: str) -> str:
        verify_data = data.get("data", {}).get("data", {}).get("verify_chumts")
        
        if not verify_data:
            return f"❌ *No UPI records found for* `{query}`"
        
        # Handle both list and dict response
        if isinstance(verify_data, list):
            if not verify_data:
                return f"❌ *No records found for* `{query}`"
            result = verify_data[0]
        elif isinstance(verify_data, dict):
            result = verify_data
        else:
            return f"❌ *Invalid response format for* `{query}`"
        
        return (
            "💸 *UPI VERIFICATION*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Account Holder:* `{result.get('name', 'N/A')}`\n"
            f"🔗 *VPA:* `{result.get('vpa', query)}`\n"
            f"🏦 *Bank:* `{result.get('bank', 'N/A')}`\n"
            f"🏛 *IFSC:* `{result.get('ifsc', 'N/A')}`\n"
            f"💳 *Account:* `{result.get('acc_no', 'N/A')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Response: {response_time} | 📅 {timestamp}"
        )
    
    @staticmethod
    def _format_pan_response(data: Dict, query: str, timestamp: str, response_time: str) -> str:
        result_data = data.get("data", {}).get("result")
        
        if not result_data:
            return f"❌ *No PAN records found for* `{query}`"
        
        # Handle both list and dict response
        if isinstance(result_data, list):
            if not result_data:
                return f"❌ *No records found for* `{query}`"
            result = result_data[0]
        elif isinstance(result_data, dict):
            result = result_data
        else:
            return f"❌ *Invalid response format for* `{query}`"
        
        return (
            "🪪 *PAN CARD VERIFICATION*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Full Name:* `{result.get('fullName', 'N/A')}`\n"
            f"🧾 *PAN Number:* `{result.get('pan', query)}`\n"
            f"📅 *Date of Birth:* `{result.get('dob', 'N/A')}`\n"
            f"📌 *Status:* `{result.get('panStatus', 'N/A')}`\n"
            f"🏛 *Category:* `{result.get('category', 'N/A')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Response: {response_time} | 📅 {timestamp}"
        )

# ================= COMMAND WRAPPERS =================
async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await LookupHandler._perform_lookup(
        update, context, "mobile", "mobile", 
        "📱 Fetching mobile number details..."
    )

async def gaadi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await LookupHandler._perform_lookup(
        update, context, "vehicle", "vehicle",
        "🚗 Fetching vehicle registration details..."
    )

async def adhar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await LookupHandler._perform_lookup(
        update, context, "aadhaar", "aadhaar",
        "🆔 Fetching Aadhaar details..."
    )

async def upi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await LookupHandler._perform_lookup(
        update, context, "upi", "upi",
        "💸 Verifying UPI details..."
    )

async def pan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await LookupHandler._perform_lookup(
        update, context, "pan", "pan",
        "🪪 Verifying PAN card details..."
    )

async def chatid_admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        await update.message.reply_text("❌ This command works only in groups.")
        return

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
    except Exception:
        await update.message.reply_text("❌ Error checking admin status.")
        return

    if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
        await update.message.reply_text("❌ Sirf group admin is command ko use kar sakta hai.")
        return

    text = (
        f"📌 Group Name: {chat.title}\n"
        f"🆔 Chat ID: `{chat.id}`\n"
        f"👤 Requested by: {user.first_name}"
    )

    await update.message.reply_text(text, parse_mode="Markdown")

# ================= ERROR HANDLER =================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        error_msg = (
            "⚠️ *Error Occurred*\n\n"
            "An error occurred while processing your request.\n\n"
            "Please try again later."
        )
        
        if update and update.effective_message:
            await update.effective_message.reply_text(error_msg, parse_mode="Markdown")
    except Exception:
        pass

# ================= BOT SETUP =================
def setup_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & ~filters.User(ADMIN_ID) & ~filters.COMMAND,
        private_block
    ))
    
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("num", num_command))
    application.add_handler(CommandHandler("gaadi", gaadi_command))
    application.add_handler(CommandHandler("adhar", adhar_command))
    application.add_handler(CommandHandler("upi", upi_command))
    application.add_handler(CommandHandler("pan", pan_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("chatid", chatid_admin_only))
    
    application.add_error_handler(error_handler)
    
    return application

# ================= MAIN EXECUTION =================
def main():
    print("=" * 50)
    print("🤖 SECRET PLATFORM BOT")
    print("=" * 50)
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"👥 Allowed Groups: {len(ALLOWED_GROUPS)}")
    print("=" * 50)
    print("✅ Bot is starting...")
    
    app = setup_bot()
    
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == "__main__":
    main()
