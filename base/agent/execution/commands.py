class Command:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __str__(self):
        return f'({self.name} {" ".join(map(str, self.args))})'


class Kick(Command):
    def __init__(self, *args):
        Command.__init__(self, 'kick', *args)


if __name__ == '__main__':
    print(Kick(1, 2))
