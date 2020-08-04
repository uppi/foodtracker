#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import os

from ratestorage import RateStorage, Rate

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

QUESTIONS = [
    ("качество еды", "избыточная", "здоровая"),
    ("употребление алкоголя", "не пил", "выпил много"),
    ("физические нагрузки", "сидел весь день", "хорошо потренировался"),
]

logger = logging.getLogger(__name__)
rate_storage = RateStorage('db.db')
rate_storage.init_db()


def question(kind):
    for qkind, bad, good in QUESTIONS:
        if kind == qkind:
            return qkind, bad, good
    logger.warning(f'no question kind {kind}')
    return '?', '?', '?'


def start(update, context):
    date = str(datetime.date.today())
    user_id = update.message.from_user.id
    rates = rate_storage.get_rates(
        user_id, date, date
    )
    rates_str = "Current:" + ",".join(map(str, rates))
    update.message.reply_text(rates_str)
    for kind, bad, good in QUESTIONS:
        send_query(update, kind, bad, good, date)


def create_keyboard(kind, date):
    return [[InlineKeyboardButton(str(i), callback_data=f'{kind},{date},{i}') for i in range(1, 6)]]


def send_query(update, kind, bad, good, date):
    reply_markup = InlineKeyboardMarkup(create_keyboard(kind, date))
    update.message.reply_text(
        f'Оцените {kind} {date} по шкале от 1 ({bad}) до 5 ({good})',
        reply_markup=reply_markup
    )


def button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    kind, date, rating = query.data.split(",")
    if rating == '0':
        kind, bad, good = question(kind)
        reply_markup = InlineKeyboardMarkup(create_keyboard(kind, date))
        query.edit_message_text(
            f'Оцените {kind} {date} по шкале от 1 ({bad}) до 5 ({good})',
            reply_markup=reply_markup
        )
    else:
        rate_storage.store_rate(Rate(user_id, date, kind, int(rating)))
        query.edit_message_text(
            text=f"{date} {kind}: {rating}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Обновить", callback_data=f'{kind},{date},0')]]
            )
        )


def main():
    updater = Updater(os.environ["TOKEN"], use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
