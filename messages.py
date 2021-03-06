import copy
from collections import defaultdict

import datetime
import io

import plotly.graph_objects as go

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


def stats_text(stats, caption):
    stats = {kind: list(map(lambda r: r.value, rates)) for kind, rates in stats.items()}
    lines = list(sorted(f'{kind}: {_mean(values):.2f} {RATE_EMOJIS[int(round(_mean(values)))]}'
                        for kind, values in stats.items()))
    rates_str = "\n".join([caption] + lines)
    return rates_str


def draw_stats(stats):
    fig = go.Figure()

    colors = [
        "#636EFA",
        "#EF553B",
        "#00CC96",
        "#AB63FA",
        "#FFA15A",
        "#19D3F3",
        "#FF6692",
        "#B6E880",
        "#FF97FF",
        "#FECB52",
    ]  # plotly.express.colors.qualitative.Plotly
    for (col, rates), color in zip(stats.items(), colors):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Scatter(x=[r.date for r in rates], y=[r.value for r in rates], name=col,
                                 fill='tozeroy', fillcolor=f'rgba({r}, {g}, {b}, 0.2)'))
    fig.update_layout(yaxis=dict(range=[0.9, 5.1]))
    buffer = io.BytesIO()
    fig.write_image(buffer, format='png', engine='kaleido')
    buffer.seek(0)
    return buffer


def moving_avg(rates, window_size):
    window = []
    result = []
    for rate in rates:
        window.append(rate.value)
        if len(window) > window_size:
            window.pop(0)
        value = sum(window) / len(window)
        rate = copy.copy(rate)
        rate.value = value
        result.append(rate)
    return result


def unsubscribed_message():
    return "Вы отписались от бота. Чтобы переподписаться, нажмите /start"
