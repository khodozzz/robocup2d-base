from base.agent.agent import Agent
from base.agent.execution.commands import Command
from base.agent.execution.execution import Execution
from base.agent.perception.perception import Perception
from base.agent.thinking.thinking import Thinking


class MyWorldModel:
    time = None


class MyThinking(Thinking):
    def __init__(self, agent, wm):
        Thinking.__init__(self, agent)

        self.wm = wm

        self.clockwise = True
        self.moved = False

    def think(self):
        self.agent.sense_body_event.clear()
        self.agent.sense_body_event.wait()

        self.agent.see_event.clear()
        self.agent.see_event.wait()

        if self.wm.time % 10 == 1:
            self.clockwise = not self.clockwise

        if not self.moved:
            self.agent.execute_command(Command('move', -5, 0))
            self.agent.execute_command(Command('change_view', 'narrow', 'high'))
            self.moved = True
        elif self.clockwise:
            self.agent.execute_command(Command('turn', 45))
        else:
            self.agent.execute_command(Command('turn', -45))


class MyPerception(Perception):
    def __init__(self, agent, wm):
        Perception.__init__(self, agent)
        self.wm = wm

    def handle_sense_body(self, msg_time, sense_body):
        self.wm.time = msg_time


if __name__ == '__main__':
    agent = Agent('LETIgers')
    agent.execution = Execution(agent)

    wm = MyWorldModel()

    agent.perception = MyPerception(agent, wm)
    agent.thinking = MyThinking(agent, wm)

    agent.run()
