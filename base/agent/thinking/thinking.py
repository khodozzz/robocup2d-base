from threading import Thread

class Thinking(Thread):
    def __init__(self, agent):
        Thread.__init__(self)

        self.agent = agent

    def think(self):
        pass

    def run(self):
        while True:
            self.think()
