from collections import defaultdict

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def question_text(question, date):
    return (f'Оцените {question.kind} {date}'
            f' по шкале от 1 ({question.bad_description}) до 5 ({question.good_description})')


RATE_EMOJIS = ["❓", "⛈", "🌧", "☁️", "🌤", "☀️"]


def _answer_str(i):
    if i in (1, 5):
        return str(i) + " " + RATE_EMOJIS[i]
    return str(i)


def question_markup(kind, date):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(_answer_str(i), callback_data=f'{kind},{date},{i}') for i in range(1, 6)]]
    )


def resubmit_markup(date, kind):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Обновить", callback_data=f'{kind},{date},0')]]
    )


def _mean(values):
    if not values:
        return 0
    else:
        return sum(values) / len(values)


def stats_text(user_id, rate_storage, start_date, end_date):
    rates = rate_storage.get_rates(
        user_id, start_date, end_date
    )
    values_by_kind = defaultdict(list)
    for rate in rates:
        values_by_kind[rate.kind].append(rate.value)
    lines = list(sorted(f'{kind}: {_mean(values):.2f} {RATE_EMOJIS[int(round(_mean(values)))]}'
                        for kind, values in values_by_kind.items()))
    rates_str = "\n".join(["За последнюю неделю:"] + lines)
    return rates_str


def unsubscribed_message():
    return "Вы отписались от бота. Чтобы переподписаться, нажмите /start"
