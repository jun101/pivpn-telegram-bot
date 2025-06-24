# bot/telegram_bot.py

import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from bot.config import TELEGRAM_BOT_TOKEN, BOT_ADMIN_ID
from bot.utils.logger import logger
from bot.utils.qrcode_generator import QRCodeGenerator

ASK_PROFILE_NAME = 1

class TelegramBot:
    def __init__(self, pivpn_manager):
        self.pivpn = pivpn_manager
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.button_handler, pattern="create")],
            states={
                ASK_PROFILE_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_profile_name)
                ],
            },
            fallbacks=[],
            per_user=True,
            per_chat=True,
        )

        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.button_handler, pattern="^(list|show_.*|revoke|revoke_.*|back)$"))
        self.app.add_handler(conv_handler)

        logger.info("TelegramBot initialized")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != BOT_ADMIN_ID:
            await update.message.reply_text("Unauthorized user.")
            logger.warning(f"Unauthorized user {user_id} tried to use /start.")
            return

        await self.show_main_menu(update)

    async def show_main_menu(self, update_or_query):
        keyboard = [
            [InlineKeyboardButton("Create VPN Profile", callback_data="create")],
            [InlineKeyboardButton("List Profiles", callback_data="list")],
            [InlineKeyboardButton("Revoke VPN Profile", callback_data="revoke")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if hasattr(update_or_query, "message") and update_or_query.message:
            await update_or_query.message.reply_text("Welcome! Choose an action:", reply_markup=reply_markup)
        else:
            await update_or_query.edit_message_text("Welcome! Choose an action:", reply_markup=reply_markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()  # acknowledge callback query

        user_id = query.from_user.id
        if user_id != BOT_ADMIN_ID:
            await query.edit_message_text("Unauthorized user.")
            logger.warning(f"Unauthorized user {user_id} tried to press buttons.")
            return ConversationHandler.END

        data = query.data

        if data == "create":
            await query.edit_message_text("Please send me the VPN profile name:")
            return ASK_PROFILE_NAME

        elif data == "list":
            profiles = self.pivpn.list_profiles()
            if not profiles:
                await query.edit_message_text("No VPN profiles found.")
                return ConversationHandler.END

            keyboard = [
                [InlineKeyboardButton(name, callback_data=f"show_{name}")] for name in profiles
            ]
            keyboard.append([InlineKeyboardButton("Back to Menu", callback_data="back")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text("Existing VPN Profiles (click to show QR code):", reply_markup=reply_markup)
            return ConversationHandler.END

        elif data.startswith("show_"):
            profile_name = data[len("show_"):]
            conf_path = os.path.join(self.pivpn.config_dir, f"{profile_name}.conf")
            if not os.path.isfile(conf_path):
                await query.edit_message_text(f"Config file not found for profile '{profile_name}'.")
                return ConversationHandler.END

            with open(conf_path, "r") as f:
                config_content = f.read()

            qr_image = QRCodeGenerator.generate_qr(config_content)

            keyboard = [
                [InlineKeyboardButton("Back to Profiles", callback_data="list")],
                [InlineKeyboardButton("Back to Menu", callback_data="back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_media(
                media=InputMediaPhoto(qr_image),
                reply_markup=reply_markup
            )
            return ConversationHandler.END

        elif data == "back":
            await self.show_main_menu(query)
            return ConversationHandler.END

        elif data == "revoke":
            await query.edit_message_text(
                "To revoke a profile, please use the 'List Profiles' option and choose the profile."
            )
            return ConversationHandler.END

        elif data.startswith("revoke_"):
            profile_name = data[len("revoke_"):]
            success = self.pivpn.revoke_profile(profile_name)
            if success:
                await query.edit_message_text(f"VPN profile revoked: {profile_name}")
            else:
                await query.edit_message_text(f"No VPN profile found: {profile_name}")
            await self.show_main_menu(query)
            return ConversationHandler.END

        else:
            await query.edit_message_text("Unknown command.")
            return ConversationHandler.END

    async def receive_profile_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        profile_name = update.message.text.strip()
        user_id = update.effective_user.id

        if not profile_name.isalnum():
            await update.message.reply_text("Profile name must be alphanumeric. Try again:")
            return ASK_PROFILE_NAME

        conf_path = self.pivpn.add_profile(profile_name)
        if not conf_path or not os.path.isfile(conf_path):
            await update.message.reply_text("Failed to create VPN profile.")
            return ConversationHandler.END

        with open(conf_path, "r") as f:
            config_content = f.read()

        qr_image = QRCodeGenerator.generate_qr(config_content)

        await update.message.reply_photo(
            photo=qr_image,
            caption=f"VPN profile created: {profile_name}\nConfig file: {conf_path}",
        )
        logger.info(f"Created VPN profile '{profile_name}' for user {user_id}")

        await self.show_main_menu(update)

        return ConversationHandler.END

    def run(self):
        logger.info("Starting Telegram bot polling...")
        self.app.run_polling()
