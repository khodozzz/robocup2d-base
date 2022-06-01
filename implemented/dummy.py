from base.agent.agent import Agent
from base.agent.execution.commands import Command
from base.agent.execution.execution import Execution
from base.agent.perception.perception import Perception
from base.agent.thinking.thinking import Thinking


class DummyThinking(Thinking):
    def __init__(self, agent):
        Thinking.__init__(self, agent)

        self.is_moved = False

    def think(self):
        self.agent.sense_body_event.clear()
        self.agent.sense_body_event.wait()

        self.agent.see_event.clear()
        self.agent.see_event.wait()

        if not self.is_moved:
            self.agent.execute_command(Command('move', -5, 0))
            self.agent.execute_command(Command('change_view', 'narrow', 'high'))
            self.is_moved = True
        else:
            self.agent.execute_command(Command('turn', 45))


if __name__ == '__main__':
    agent = Agent('LETIgers')
    agent.perception = Perception(agent)
    agent.execution = Execution(agent)

    agent.thinking = DummyThinking(agent)

    agent.run()
