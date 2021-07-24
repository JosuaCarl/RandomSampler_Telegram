from random import *
import datetime


class RandoJob:

    def __init__(self, start=None, end=None, questions=None, answers=None, frequencies=[]):
        self.start = start
        self.end = end
        self.qa = dict()
        self.frequencies = frequencies
        self.qa_in_order = []
        self.scheduled_times = []
        self.ready = False
        self.queued_questions = []
        self.check_ready()

    def set_start(self, start):
        self.start = start
        self.check_ready()

    def set_end(self, end):
        self.end = end
        self.check_ready()

    def set_qa(self, question, answers):
        self.qa[question] = answers
        self.check_ready()

    def set_frequencies(self, frequency: int):
        self.frequencies.append(frequency)
        self.check_ready()

    def reset_qa(self):
        self.qa_in_order = []
        self.qa_in_order = []

    def schedule(self):
        # make list of random order of questions
        for i in range(0, len(self.frequencies)):
            if self.queued_questions.__contains__(i):
                continue
            self.queued_questions.append(i)
            for j in range(0, self.frequencies[i]):
                question = list(self.qa.keys())[i] + "?"
                self.qa_in_order.append({question: list(self.qa.values())[i]})
        self.qa_in_order = sample(self.qa_in_order, len(self.qa_in_order))

        # checks for valid start & end time
        if self.start < datetime.datetime.now():
            self.start = datetime.datetime.now()
            self.start.minutes = self.start.minutes + 1
        if self.end < self.start:
            self.end.minutes = self.start.minutes + 1

        # calculates time difference
        time_difference = self.end - self.start
        time_to_start = self.start - datetime.datetime.now()
        for i in range(0, len(self.qa_in_order)):
            waiting_time = random() * time_difference
            waiting_time = time_to_start + waiting_time
            waiting_time = waiting_time.total_seconds()
            self.scheduled_times.append(waiting_time)

    def check_ready(self):
        if len(self.qa) > 0:
            print("qa ready")
            if len(self.frequencies) > 0:
                print("freq ready")
                if self.start is not None:
                    print("start ready")
                    if self.end is not None:
                        print("end ready")
                        self.schedule()
                        self.ready = True
