from time import sleep
from threading import Thread, Event

from base.agent.execution.commands import Command


class Execution(Thread):
    def __init__(self, agent):
        Thread.__init__(self)

        self.agent = agent
        self.commands = []

    def add_command(self, command: Command):
        self.commands.append(command)

    def run(self):
        while True:
            self.agent.sense_body_event.clear()
            self.agent.sense_body_event.wait()
            self.commands = []
            sleep(0.08)
            self.agent.sendto(' '.join(map(str, self.commands)), self.agent.server_addr)
            # print('EXECUTION:', ' '.join(map(str, self.commands)))
