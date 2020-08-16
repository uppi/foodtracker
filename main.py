#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import logging

from messages import question_text, question_markup, resubmit_markup, stats_text, unsubscribed_message, draw_stats
from storage import Storage, QUESTIONS, question_by_kind
from model import Rate

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

storage = Storage(os.environ["DB"])
storage.init_db()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def start(update, context):
    date = datetime.date.today()
    user_id = update.message.from_user.id

    storage.store_user(user_id)
    for question in QUESTIONS:
        update.message.reply_text(
            question_text(question, date),
            reply_markup=question_markup(question.kind, date)
        )


def stats(update, context):
    date = datetime.date.today()
    user_id = update.message.from_user.id
    stats_values = storage.get_stats(str(date - datetime.timedelta(days=7)), str(date), user_id)
    update.message.bot.sendPhoto(
        user_id,
        draw_stats(stats_values, date),
        caption=stats_text(stats_values)
    )


def stop(update, context):
    user_id = update.message.from_user.id
    storage.remove_user(user_id)
    update.message.reply_text(unsubscribed_message())


def button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    kind, date, rating = query.data.split(",")
    if rating == '0':
        question = question_by_kind(kind)
        query.edit_message_text(
            question_text(question, date),
            reply_markup=question_markup(question.kind, date)
        )
    else:
        storage.store_rate(Rate(user_id, date, kind, int(rating)))
        query.edit_message_text(
            text=f"{date} {kind}: {rating}",
            reply_markup=resubmit_markup(date, kind)
        )


def main():
    updater = Updater(os.environ["TOKEN"], use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('stats', stats))
    updater.dispatcher.add_handler(CommandHandler('stop', stop))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
