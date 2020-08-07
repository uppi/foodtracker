# Foodtracker

Telegram bot to track everyday quality of food, sleep, sports, etc.

In Russian.

Hosted at [@food_mood_tracker_bot](http://t.me/food_mood_tracker_bot)

Consists of 2 parts:
- running main.py
- crontab with sender.py once a day, e. g. `30 22 * * *     cd /home/uppi/workspace/foodtracker && python3 sender.py`
