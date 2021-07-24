#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import datetime
import RandoJob
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.

randoJobs = [RandoJob.RandoJob()]
current_message = "Message not replaced."


def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text(
        'Hi! Use /set_start_datetime <dd.mm.yyyy hh:mm index> (e.g. 12.03.2020 12:30 12) to set a '
        'starting point for random sampeling. \n'
        'Use /set_end_datetime <dd.mm.yyyy hh:mm index> (e.g. 12.03.2020 12:31 12) to set a '
        'end point for random sampeling. \n'
        'Use /unset to delete all  samples\n'
        'Use /add_qa <FoO Bar Bam ? bla bla; Bla blUbb; blUbb Bla ,index> to define your question'
        'and answers.')


def set_start_datetime(update: Update, context: CallbackContext, index=(len(randoJobs) - 1)) -> None:
    """Add a starttime to the queue."""
    chat_id = update.message.chat_id
    # try:
    # Handles input string
    input_string_date = context.args[0]
    input_string_time = context.args[1]

    if len(context.args) > 2:
        input_string_index = context.args[2]

        # extracts index
        index = int(input_string_index)

    # extracts date
    input_string_date = input_string_date.split(" ")
    start_date = input_string_date[0].split(".")
    start_date = datetime.date(int(start_date[2]), int(start_date[1]), int(start_date[0]))

    # extract time
    start_time = input_string_time.split(":")
    start_time = datetime.time(int(start_time[0]), int(start_time[1]))
    start_datetime = datetime.datetime.combine(date=start_date, time=start_time)

    if start_datetime < datetime.datetime.now():
        update.message.reply_text('Sorry we can not go back to future!')
        return

    # appends to global jobs
    randoJobs[index].set_start(start_datetime)

    text = 'Starting point of position ' + str(index) + '  successfully set!'

    context.job_queue.job_removed = remove_job_if_exists(str(chat_id), context)
    if context.job_queue.job_removed:
        text += ' Old one was removed.'
    update.message.reply_text(text)

    if randoJobs[index].ready:
        schedule_question(update, context, index)

    # except (IndexError, ValueError):
    #     update.message.reply_text('Usage: /set_start_datetime <dd.mm.yyyy hh:mm index>')


def set_end_datetime(update: Update, context: CallbackContext, index=(len(randoJobs) - 1)) -> None:
    """Add a starttime to the queue."""
    chat_id = update.message.chat_id
    # try:
    # Handles input string
    input_string_date = context.args[0]
    input_string_time = context.args[1]

    if len(context.args) > 2:
        input_string_index = context.args[2]

        # extracts index
        index = int(input_string_index)

    # extracts date
    input_string_date = input_string_date.split(" ")
    end_date = input_string_date[0].split(".")
    end_date = datetime.date(int(end_date[2]), int(end_date[1]), int(end_date[0]))

    # extract time
    end_time = input_string_time.split(":")
    end_time = datetime.time(int(end_time[0]), int(end_time[1]))
    end_datetime = datetime.datetime.combine(date=end_date, time=end_time)

    if end_datetime < datetime.datetime.now():
        update.message.reply_text('Sorry we can not go back to future!')
        return

    # appends to global jobs
    randoJobs[index].set_end(end_datetime)

    text = 'End point of position ' + str(index) + '  successfully set!'

    context.job_queue.job_removed = remove_job_if_exists(str(chat_id), context)
    if context.job_queue.job_removed:
        text += ' Old one was removed.'
    update.message.reply_text(text)

    if randoJobs[index].ready:
        schedule_question(update, context, index)

    # except (IndexError, ValueError):
    #     update.message.reply_text('Usage: /set_end_datetime <dd.mm.yyyy hh:mm index>')


def add_qa(update: Update, context: CallbackContext, index=(len(randoJobs) - 1), frequency=1) -> None:
    """Add a starttime to the queue."""
    chat_id = update.message.chat_id
    # try:
    # Handles input string
    input_string = " ".join(context.args)
    print(input_string)

    # extracts index
    if input_string.__contains__(","):
        temp_is = input_string.split(",")
        position = temp_is[1]
        frequency = temp_is[2]
        input_string = temp_is[0]
        position = int(position)

    input_string = input_string.split("?")
    question = input_string[0]
    answers = input_string[1].split(";")

    # resets schedueled times and qa_in_order
    randoJobs[index].reset_qa()

    # appends to global jobs
    randoJobs[index].set_qa(question, answers)
    randoJobs[index].set_frequencies(int(frequency))

    text = 'Q & A at position ' + str(index) + '  successfully set!'

    context.job_queue.job_removed = remove_job_if_exists(str(chat_id), context)
    if context.job_queue.job_removed:
        text += ' Old one was removed.'
    update.message.reply_text(text)

    if randoJobs[index].ready:
        schedule_question(update, context, index)

    # except (IndexError, ValueError):
    #     update.message.reply_text('Usage: /add_qa FoO Bar Bam ? bla bla; Bla blUbb; blUbb Bla ,index, frequency>')


def schedule_question(update, context: CallbackContext, index: int) -> None:
    schedule_in_sec = randoJobs[index].scheduled_times
    questions_in_order = randoJobs[index].qa_in_order

    chat_id = update.message.chat_id
    for i in range(0, len(schedule_in_sec)):
        question, answers = list(questions_in_order[i].items())[0]
        message = str(question) + "\n"
        for j in range(0, len(answers)):
            message = message + "\n" + str(j) + ". " + str(answers[j])

        print(message)
        global current_message
        current_message = message
        context.job_queue.run_once(send_message, schedule_in_sec[i], context=chat_id, name=str(chat_id))


def unset(update: Update, context: CallbackContext) -> None:
    """Remove all jobs."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


def send_message(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text=current_message)


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater('1939650983:AAEY41Nk673skF7Wp8HkJ5TZeltelF-VuYo')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set_start_datetime", set_start_datetime))
    dispatcher.add_handler(CommandHandler("set_end_datetime", set_end_datetime))
    dispatcher.add_handler(CommandHandler("add_qa", add_qa))
    dispatcher.add_handler(CommandHandler("unset", unset))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
