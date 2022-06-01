from time import sleep

from threading import Event

from base.agent.execution.execution import Execution
from base.agent.perception.perception import Perception
from base.agent.thinking.thinking import Thinking
from base.agent.udpclient import UDPClient


class Agent(UDPClient):
    def __init__(self, team, goalie=False,
                 perceprion=None, thinking=None, execution=None):
        UDPClient.__init__(self)

        self.team = team
        self.goalie = goalie

        self.perception = perceprion
        self.thinking = thinking
        self.execution = execution

        self.server_addr = ('localhost', 6000)

        self.sense_body_event = Event()
        self.see_event = Event()

    def run(self):
        self._init_server()

        self.execution.start()
        self.thinking.start()
        self.perception.start()

    def execute_command(self, command):
        self.execution.add_command(command)

    def _init_server(self):
        self.sendto(f'(init {self.team})', self.server_addr)
        msg, self.server_addr = self.recvfrom()
        print(msg)
        sleep(1)


if __name__ == '__main__':
    agent = Agent('LETIgers')
    agent.perception = Perception(agent)
    agent.thinking = Thinking(agent)
    agent.execution = Execution(agent)

    agent.run()
