#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import logging

from messages import question_text, question_markup, resubmit_markup, stats_text, unsubscribed_message, draw_stats, \
    moving_avg
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


def moving_avg_stats(update, context):
    date = datetime.date.today()
    user_id = update.message.from_user.id
    stats_values = storage.get_stats(date - datetime.timedelta(days=36), date, user_id)
    moving_avg_stats_values = {
        key: moving_avg(value, 7)[-30:]
        for key, value in stats_values.items()
    }
    update.message.bot.sendPhoto(
        user_id,
        draw_stats(moving_avg_stats_values),
        caption=stats_text(stats_values, "За последний месяц:")
    )


def stats(update, context):
    date = datetime.date.today()
    user_id = update.message.from_user.id
    stats_values = storage.get_stats(date - datetime.timedelta(days=7), date, user_id)
    stats_values = {
        key: value[-7:]
        for key, value in stats_values.items()
    }
    update.message.bot.sendPhoto(
        user_id,
        draw_stats(stats_values),
        caption=stats_text(stats_values, "За последнюю неделю:")
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
        rating = int(rating)
        storage.store_rate(Rate(user_id, date, kind, rating))
        today = datetime.date.today()
        avg = storage.avg_rate(user_id, kind, today - datetime.timedelta(days=7), today)
        if avg > rating:
            mean_text = " ↘"
        elif avg < rating:
            mean_text = " ↗"
        else:
            mean_text = ""
        query.edit_message_text(
            text=f"{date} {kind}: {rating}{mean_text}",
            reply_markup=resubmit_markup(date, kind)
        )


def main():
    updater = Updater(os.environ["TOKEN"], use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('stats', stats))
    updater.dispatcher.add_handler(CommandHandler('moving_avg_stats', moving_avg_stats))
    updater.dispatcher.add_handler(CommandHandler('stop', stop))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
