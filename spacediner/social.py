import pickle
import random
from collections import OrderedDict

from . import cli
from . import diner
from . import rewards
from . import time


class Chats:
    chats = None
    done = 0

    def init(self, data):
        if data:
            self.chats = []
            for chat in data:
                self.chats.append(chat)

    def next_chat(self):
        if self.chats:
            return self.chats[self.done]

    def chat(self):
        if self.chats:
            chat = self.next_chat()
            self.done += 1
            if self.done >= len(self.chats):
                self.done = 0
            return chat


class Greetings:
    greetings = None

    def init(self, data):
        if data:
            self.greetings = []
            for greeting in data:
                self.greetings.append(greeting)

    def get(self):
        random.seed()
        return random.choice(self.greetings)


class Meeting:
    text = None
    question = None
    replies = None
    rewards = None

    def init(self, data):
        self.text = data.get('meeting')
        self.question = data.get('question')
        self.replies = []
        for reply_data in data.get('replies', []):
            self.replies.append((reply_data.get('reply'), reply_data.get('reaction')))
        random.seed()
        random.shuffle(self.replies)
        if 'rewards' in data:
            self.rewards = []
            for reward in rewards.init_list(data.get('rewards')):
                self.rewards.append(reward)

    def get_replies(self):
        return [reply for reply, _ in self.replies]

    def reaction(self, reply):
        return self.replies[reply][1]


class Friendship:
    name = None
    available = True
    days = None
    meetings = None
    meetings_done = 0

    def __init__(self, name):
        self.name = name

    def init(self, data):
        self.meetings = []
        self.available = data.get('available', True)
        self.days = data.get('days')
        if 'meetings' in data:
            for meeting_data in data.get('meetings'):
                meeting = Meeting()
                meeting.init(meeting_data)
                self.meetings.append(meeting)

    def available_today(self):
        return self.available and not self.days or time.weekday() in self.days

    def has_meeting(self):
        return self.meetings and self.meetings_done < len(self.meetings) and self.available_today()

    def get_meeting(self):
        if self.has_meeting():
            return self.meetings[self.meetings_done]

    def meet(self, reply):
        meeting = self.get_meeting()
        reaction = meeting.reaction(reply)
        cli.print_dialog(self.name, reaction)
        for reward in meeting.rewards:
            cli.wait_for_input()
            cli.print_newline()
            cli.print_dialog(self.name, reward.text)
            reward.apply()
        self.meetings_done += 1
        return reaction


class Social:
    name = None
    chats = None
    greetings = None
    friendship = None

    def init(self, data):
        self.name = data.get('name')
        if 'chats' in data:
            self.chats = Chats()
            self.chats.init(data.get('chats'))
        if 'greetings' in data:
            self.greetings = Greetings()
            self.greetings.init(data.get('greetings'))
        if 'friendship' in data:
            self.friendship = Friendship(self.name)
            self.friendship.init(data.get('friendship'))

    def next_chat(self):
        return self.chats.next_chat() if self.chats else None

    def chat(self):
        return self.chats.chat() if self.chats else None

    def greeting(self):
        return self.greetings.get() if self.greetings else None

    def has_meeting(self):
        return self.friendship and self.friendship.has_meeting()

    def get_meeting(self):
        if self.friendship:
            return self.friendship.get_meeting()

    def meet(self, reply):
        return self.friendship.meet(reply)

    def unlock_friendship(self):
        if self.friendship:
            self.friendship.available = True
            if self.friendship.has_meeting():
                cli.print_message('Meeting with {} unlocked'.format(self.name))

    def lock_friendship(self):
        if self.friendship:
            self.friendship.available = False
            if self.friendship.has_meeting():
                cli.print_message('Meeting with {} locked'.format(self.name))


social = None
chatted_today = None


def get(name):
    global social
    return social.get(name)


def chats_available():
    global social
    global chatted_today
    chats = [friend for friend, social in social.items() if friend not in chatted_today and social.next_chat()]
    return chats


def has_chats(name, group_name):
    global chatted_today
    if name in chatted_today:
        return False
    friend_social = get(group_name)
    if friend_social:
        return friend_social.chats is not None
    return False


def next_chat(name):
    return get(name).next_chat()


def chat(name, group_name):
    global chatted_today
    chatted_today.append(name)
    return get(group_name).chat()


def greeting(name):
    return get(name).greeting()


def greet_and_chat(name, group_name):
    text = chat(name, group_name)
    greeting_text = greeting(group_name)
    if greeting:
        text = '{} {}! {}'.format(greeting_text, diner.diner.chef, text)
    return text


def available_meetings():
    global social
    meetings = [friend for friend, social in social.items() if social.has_meeting()]
    return meetings


def meet(name, reply):
    global social
    return social.get(name).meet(reply)


def unlock_friendship(name):
    global social
    social.get(name).unlock_friendship()


def lock_friendship(name):
    global social
    social.get(name).lock_friendship()


def morning():
    global chatted_today
    chatted_today = []


def init(data):
    global social
    global chatted_today
    social = OrderedDict()
    for social_data in data:
        friend_social = Social()
        friend_social.init(social_data)
        social.update({friend_social.name: friend_social})
    chatted_today = []
    time.register_callback(time.Calendar.TIME_MORNING, morning)


def save(file):
    global social
    global chatted_today
    pickle.dump(social, file)
    pickle.dump(chatted_today, file)


def load(file):
    global social
    global chatted_today
    social = pickle.load(file)
    chatted_today = pickle.load(file)
    time.register_callback(time.Calendar.TIME_MORNING, morning)