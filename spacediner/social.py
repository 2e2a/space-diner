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

    def init(self, data):
        self.text = data.get('meeting')
        self.question = data.get('question')
        self.replies = []
        for reply_data in data.get('good replies', []):
            self.replies.append((reply_data.get('reply'), reply_data.get('reaction'), True))
        for reply_data in data.get('bad replies', []):
            self.replies.append((reply_data.get('reply'), reply_data.get('reaction'), False))
        random.seed()
        random.shuffle(self.replies)

    def get_replies(self):
        return [reply for reply, _, _ in self.replies]

    def reaction(self, reply):
        _, reaction, is_good = self.replies[reply]
        return reaction, is_good


class Friendship:
    meetings = None
    meetings_done = 0
    rewards = None
    level = 0
    unlocked = False

    def init(self, data):
        self.meetings = []
        if 'meetings' in data:
            for meeting_data in data.get('meetings'):
                meeting = Meeting()
                meeting.init(meeting_data)
                self.meetings.append(meeting)
        if 'rewards' in data:
            self.rewards = {}
            for reward in rewards.init_list(data.get('rewards')):
                if reward.level in self.rewards:
                    self.rewards[reward.level].append(reward)
                else:
                    self.rewards.update({reward.level: [reward]})

    def has_meeting(self):
        return self.meetings and self.meetings_done < len(self.meetings)

    def get_meeting(self):
        if self.has_meeting():
            return self.meetings[self.meetings_done]

    def meet(self, reply):
        reaction, liked = self.get_meeting().reaction(reply)
        self.meetings_done += 1
        return reaction, liked

    def level_up(self, name):
        self.level += 1
        if self.level in self.rewards:
            for reward in self.rewards.get(self.level):
                cli.print_dialog(name, reward.text)
                reward.apply()

    def was_last_meeting(self):
        return len(self.meetings) == self.meetings_done

    def unlock_all_rewards(self, name):
        for level_rewards in self.rewards.values():
            for reward in level_rewards:
                cli.print_dialog(name, reward.text)
                reward.apply()


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
            self.friendship = Friendship()
            self.friendship.init(data.get('friendship'))

    def next_chat(self):
        return self.chats.next_chat() if self.chats else None

    def chat(self):
        return self.chats.chat() if self.chats else None

    def greeting(self):
        return self.greetings.get() if self.greetings else None

    def has_meeting(self):
        return self.friendship and self.friendship.unlocked and self.friendship.has_meeting()

    def get_meeting(self):
        if self.friendship:
            return self.friendship.get_meeting()

    def meet(self, reply):
        return self.friendship.meet(reply)

    def level_up(self):
        return self.friendship.level_up(self.name)

    def was_last_meeting(self):
        return self.friendship.was_last_meeting()

    def unlock_all_rewards(self):
        return self.friendship.unlock_all_rewards(self.name)

    def unlock_friendship(self):
        if self.friendship:
            self.friendship.unlocked = True
            if self.friendship.has_meeting():
                cli.print_message('Meeting with {} unlocked'.format(self.name))

    def lock_friendship(self):
        if self.friendship:
            self.friendship.unlocked = False
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


def has_chats(name):
    global chatted_today
    if name in chatted_today:
        return False
    friend_social = get(name)
    if friend_social:
        return friend_social.chats is not None
    return False


def next_chat(name):
    return get(name).next_chat()


def chat(name):
    global chatted_today
    chatted_today.append(name)
    return get(name).chat()


def greeting(name):
    return get(name).greeting()


def greet_and_chat(name):
    text = chat(name)
    greeting_text = greeting(name)
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


def level_up(name):
    global social
    return social.get(name).level_up()


def was_last_meeting(name):
    global social
    return social.get(name).was_last_meeting()


def unlock_all_rewards(name):
    global social
    return social.get(name).unlock_all_rewards()


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
    pickle.dump(social, file)


def load(file):
    global social
    social = pickle.load(file)
