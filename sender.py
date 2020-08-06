#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os

from messages import question_text, question_markup
from storage import Storage, QUESTIONS

from telegram import Bot

storage = Storage('db.db')

bot = Bot(os.environ["TOKEN"])


def send(user_id, question, date):
    bot.sendMessage(
        user_id,
        question_text(question, date),
        reply_markup=question_markup(question.kind, date)
    )


def main():
    date = datetime.date.today()
    for user_id in storage.get_users():
        for question in QUESTIONS:
            send(user_id, question, date)


if __name__ == '__main__':
    main()
