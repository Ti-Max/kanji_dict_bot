import math
import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
import telegram
from telegram._utils.types import ReplyMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import os
from dotenv import load_dotenv
from termcolor import colored
from anki_deck_reader import read_field, search_kanji, search_radical
from anki.notes import Note
from pprint import pprint as pp

from messages import radical_message, kanji_message, remove_html

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

current_element = {}


# Define a few command handlers. These usually take the two arguments update and
# context.
# async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     await update.message.reply_html(
#         rf"Hi {user.mention_html()}!",
#         reply_markup=ForceReply(selective=True),
#     )

SHOW_KANJI, SELECT_RADICAL, SHOW_RADICAL = range(3)


async def send_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message: str,
    reply_markup: ReplyMarkup | None = None,
):
    if update.callback_query:
        # If called from a callback query, use the callback_query's message
        chat_id = update.callback_query.message.chat_id  # pyright: ignore
        await context.bot.send_message(
            chat_id=chat_id, text=message, parse_mode="HTML", reply_markup=reply_markup
        )
    elif update.message:
        # If called from a direct message
        await update.message.reply_text(
            message, parse_mode="HTML", reply_markup=reply_markup
        )


async def show_kanji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or update.message.text is None:
        return SHOW_KANJI

    try:
        kanji_note = search_kanji(update.message.text)

        if kanji_note is None:
            await update.message.reply_text(
                "Could not find this kanji or radical in WaniKani deck, try a different one"
            )
            return SHOW_KANJI
        else:
            response = kanji_message(kanji_note)

            try:
                await update.message.reply_text(response, parse_mode="HTML")
            except telegram.error.BadRequest:
                logger.warning(
                    colored(
                        f"Unsupported html tags were found in '{update.message}' card",
                        "yellow",
                    )
                )
                await update.message.reply_text(
                    f"Oooops, looks like html for this card is gone, please contact <s>our tech support team</s> me. \n\n {remove_html(response)}",
                    parse_mode="HTML",
                )

            # buttons with radicals that user can click on
            return await list_radicals(update, context, kanji_note)

    except Exception as err:
        logger.error(err)
        await update.message.reply_text("You just broke it, good job 👍")
        return SHOW_KANJI


async def list_radicals(
    update: Update, context: ContextTypes.DEFAULT_TYPE, kanji_note: Note
) -> int:
    # get all radicals in the kanji
    radicals_names = read_field(kanji_note, "Radicals_Names").split(", ")
    radicals = read_field(kanji_note, "Radicals").split(", ")
    radicals_icons_names = read_field(kanji_note, "Radicals_Icons_Names").split(", ")

    buttons_labels = []
    for i in range(len(radicals)):
        buttons_labels.append(
            {
                "label": f"{radicals[i]} ({radicals_names[i]})",
                "name": radicals_names[i],
                "radical": radicals[i],
            }
        )
    for i in range(len(radicals_icons_names)):
        if radicals_icons_names[i] != "":
            buttons_labels.append(
                {
                    "label": f"{radicals_icons_names[i]}",
                    "name": radicals_icons_names[i],
                    "radical": "",
                }
            )

    buttons = []
    grid_size = math.ceil(math.sqrt(len(buttons_labels)))

    # put buttons in a grid
    i = 0
    for row in range(grid_size):
        buttons.append([])
        for _col in range(grid_size):
            if i == len(buttons_labels):
                break

            button = InlineKeyboardButton(
                buttons_labels[i]["label"],
                callback_data=f"{buttons_labels[i]["name"]};{buttons_labels[i]["radical"]}",
            )
            buttons[row].append(button)
            i += 1

    # create buttons
    keyboardMarkup = InlineKeyboardMarkup(buttons)
    await send_message(
        update,
        context,  # pyright: ignore
        f"Lookup radicals for <code>{read_field(kanji_note, "Kanji")}</code> ⬇️",
        reply_markup=keyboardMarkup,
    )
    context.user_data["current_kanji"] = kanji_note  # pyright: ignore

    return SELECT_RADICAL


async def select_radical(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()  # pyright: ignore
    await query.edit_message_text(
        text=f"Searching <code>{query.data.split(";")[1]}</code> ({query.data.split(";")[0]}) 🔄",
        parse_mode="HTML",
    )  # pyright: ignore

    return await show_radical(update, context, query.data)  # pyright: ignore


async def show_radical(
    update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str | None = None
) -> int:
    if callback_data is None:
        query_radical = update.message.text  # pyright: ignore
        query_name = update.message.text  # pyright: ignore

    else:
        # super bad hack
        query_name = callback_data.split(";")[0]  # pyright: ignore
        query_radical = callback_data.split(";")[1]

    try:
        radical_note = search_radical(query_name, query_radical)  # pyright: ignore

        if radical_note is None:
            await send_message(
                update,
                context,
                "Could not find this radical in WaniKani deck, try a different one",
            )
            return SHOW_KANJI
        else:
            response = radical_message(radical_note)

            try:
                await send_message(update, context, response)
            except telegram.error.BadRequest:
                logger.warning(
                    colored(
                        f"Unsupported html tags were found in '{query_name}' card",
                        "yellow",
                    )
                )
                await send_message(
                    update,
                    context,
                    f"Oooops, looks like html for this card is gone, please contact <s>our tech support team</s> me. \n\n {remove_html(response)}",
                )

            if "current_kanji" in context.user_data:  # pyright: ignore
                # buttons with radicals that user can click on
                return await list_radicals(
                    update,
                    context,
                    context.user_data["current_kanji"],  # pyright: ignore
                )
            else:
                return SHOW_KANJI

    except Exception as err:
        logger.error(err)
        await send_message(update, context, "You just broke it, good job 👍")
        return SHOW_KANJI


async def cancel(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(  # pyright: ignore
        "Bye! Hope to talk to you again soon.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ["TOKEN"]).build()

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start))

    # application.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, show_kanji)],
        states={
            SHOW_KANJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_kanji)],
            # LIST_RADICALS: [CallbackQueryHandler(button)],
            SELECT_RADICAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_kanji),
                CallbackQueryHandler(select_radical),
            ],
            SHOW_RADICAL: [CallbackQueryHandler(show_radical)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # every new message is a new kanji to search
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_kanji))
    # application.add_handler(CallbackQueryHandler())

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
