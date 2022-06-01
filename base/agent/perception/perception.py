from threading import Thread, Event

from base.agent.perception.message_parser import MessageParser


class Perception(Thread):
    def __init__(self, agent):
        Thread.__init__(self)

        self.agent = agent

    def handle_msg(self, msg):
        # print('PERCEPTION:', msg)
        parser = MessageParser()
        msg_type, msg_time, data = parser.parse(msg)

        if msg_type == 'sense_body':
            self.agent.sense_body_event.set()
            self.handle_see(msg_time, data)
        elif msg_type == 'see':
            self.agent.see_event.set()
            self.handle_sense_body(msg_time, data)

    def handle_see(self, msg_time, objects):
        pass

    def handle_sense_body(self, msg_time, sense_body):
        pass

    def run(self):
        while True:
            msg, addr = self.agent.recvfrom()
            self.handle_msg(msg)
