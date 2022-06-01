import re
from base.soccer.objects import *
from base.soccer.sense_body import *


class MessageParser:
    PATTERN_INT = re.compile("^-?\d+$")
    PATTERN_FLOAT = re.compile("^-?\d*[.]\d+$")

    def parse(self, msg):
        # get all the expressions contained in the given message
        linked = self._link_text(msg)

        # this is the name of the function that should be used to handle
        # this message type.  we pull it from this object dynamically to
        # avoid having a huge if/elif/.../else statement.
        msg_func = "_parse_%s" % linked[0]

        if hasattr(self, msg_func):
            # call the appropriate function with this message
            return getattr(self, msg_func).__call__(linked)

    def _link_text(self, text):
        """
        Ex: "(baz 0 (foo 1.5))" becomes ['baz', 0, ['foo', 1.5]].
        """

        # make sure all of our parenthesis match
        if text.count("(") != text.count(")"):
            raise ValueError("Message text has unmatching parenthesis!")

        # result acts as a stack that holds the strings grouped by nested parens.
        # result will only ever contain one item, the first level of indenting
        # encountered.  this is because the server (hopefully!) only ever sends one
        # message at a time.
        result = []

        # the current level of indentation, used to append chars to correct level
        indent = 0

        # the non-indenting characters we find. these are kept in a buffer until
        # we indent or dedent, and then are added to the current indent level all
        # at once, for efficiency.
        s = []

        # whether we're currently in the middle of parsing a string
        in_string = False

        # the last character seen, None to begin with
        prev_c = None
        for c in text:
            # prevent parsing parens when inside a string (also ignores escaped
            # '"'s as well). doesn't add the quotes so we don't have to recognize
            # that value as a string via a regex.
            if c == '"' and prev_c != "\\":
                in_string = not in_string

            # we only indent/dedent if not in the middle of parsing a string
            elif c == "(" and not in_string:
                # recurse into current level of nesting
                cur = result
                for i in range(indent):
                    cur = cur[-1]

                # add our buffered string onto the previous level, then clear it
                # for the next.
                if len(s) > 0:
                    val = ''.join(s)

                    # try to convert our string into a value and append it to our
                    # list.  failing that, simply append it as an attribute name.
                    if self.PATTERN_INT.match(val):
                        cur.append(int(val))
                    elif self.PATTERN_FLOAT.match(val):
                        cur.append(float(val))
                    else:
                        cur.append(val)

                    s = []

                # append a new level of nesting to our list
                cur.append([])

                # increase the indent level so we can get back to this level later
                indent += 1

            elif c == ")" and not in_string:
                # append remaining string buffer before dedenting
                if len(s) > 0:
                    cur = result
                    for i in range(indent):
                        cur = cur[-1]

                    val = ''.join(s)

                    # try to convert our string into a value and append it to our
                    # list.  failing that, simply append it as an attribute name.
                    if self.PATTERN_INT.match(val):
                        cur.append(int(val))
                    elif self.PATTERN_FLOAT.match(val):
                        cur.append(float(val))
                    else:
                        cur.append(val)

                    s = []

                # we finished with one level, so dedent back to the previous one
                indent -= 1

            # append non-space characters to the buffer list. spaces are delimiters
            # for expressions, hence are special.
            elif c != " ":
                # append the current string character to the buffer list.
                s.append(c)

            # we separate expressions by spaces
            elif c == " " and len(s) > 0:
                cur = result
                for i in range(indent):
                    cur = cur[-1]

                val = ''.join(s)

                # try to convert our string into a value and append it to our
                # list.  failing that, simply append it as an attribute name.
                if self.PATTERN_INT.match(val):
                    cur.append(int(val))
                elif self.PATTERN_FLOAT.match(val):
                    cur.append(float(val))
                else:
                    cur.append(val)

                s = []

            # save the previous character. used to determine if c is escaped
            prev_c = c

        # this returns the first and only message found.  result is a list simply
        # because it makes adding new levels of indentation simpler as it avoids
        # the 'if result is None' corner case that would come up when trying to
        # append the first '('.
        return result[0]

    def _parse_see(self, msg):
        ball = None
        flags = []
        goals = []
        lines = []
        players = []

        # iterate over all the objects given to us in the last see message
        for obj in msg[2:]:
            name = obj[0]
            members = obj[1:]

            # get basic information from the object.  different numbers of
            # parameters (inconveniently) specify different types and
            # arrangements of data received for the object.

            # default values for object data
            distance = None
            direction = None
            dist_change = None
            dir_change = None
            body_dir = None
            neck_dir = None

            # a single item object means only direction
            if len(members) == 1:
                direction = members[0]

            # objects with more items follow a regular pattern
            elif len(members) >= 2:
                distance = members[0]
                direction = members[1]

                # include delta values if present
                if len(members) >= 4:
                    dist_change = members[2]
                    dir_change = members[3]

                # include body/neck values if present
                if len(members) >= 6:
                    body_dir = members[4]
                    neck_dir = members[5]

            # parse flags
            if name[0] == 'f':
                # since the flag's name sometimes contains a number, the parser
                # recognizes it as such and converts it into an int.  it's
                # always the last item when it's a number, so we stringify the
                # last item of the name to convert any numbers back.
                name[-1] = str(name[-1])

                # the flag's id is its name's members following the f as a string
                flag_id = ''.join(name[1:])

                flags.append(Flag(distance, direction, flag_id))

            # parse players
            elif name[0] == 'p':
                # extract any available information from the player object's name
                teamname = None
                uniform_number = None

                if len(name) >= 2:
                    teamname = name[1]
                if len(name) >= 3:
                    uniform_number = name[2]
                if len(name) >= 4:
                    position = name[3]

                # calculate player's speed
                speed = None
                # TODO: calculate player's speed!

                players.append(Player(distance, direction,
                                      dist_change, dir_change, speed, teamname,
                                      uniform_number, body_dir, neck_dir))

            # parse goals
            elif name[0] == 'g':
                # see if we know which side's goal this is
                goal_id = None
                if len(name) > 1:
                    goal_id = name[1]

                goals.append(Goal(distance, direction, goal_id))

            # parse lines
            elif name[0] == 'l':
                # see if we know which line this is
                line_id = None
                if len(name) > 1:
                    line_id = name[1]

                lines.append(Line(distance, direction, line_id))

            # parse the ball
            elif name[0] == 'b':
                ball = Ball(distance, direction, dist_change, dir_change)

            # object very near to but not viewable by the player are 'blank'
            elif name[0] == 'B':
                # the out-of-view ball
                ball = Ball(None, None, None, None)
            elif name[0] == 'F':
                # an out-of-view flag
                flags.append(Flag(None, None, None))
            elif name[0] == 'G':
                # an out-of-view goal
                goals.append(Goal(None, None, None))
            elif name[0] == 'P':
                # an out-of-view player
                players.append(Player(None, None, None, None, None, None, None, None, None))

        return msg[0], msg[1], (ball, players, flags, lines, goals)

    def _parse_sense_body(self, msg):
        """
        Deals with the agent's body model information.
        """

        view_quality = None
        view_width = None
        stamina = None
        effort = None
        speed_amount = None
        speed_direction = None
        neck_direction = None

        for info in msg[2:]:
            name = info[0]
            values = info[1:]

            if name == "view_mode":
                view_quality = values[0]
                view_width = values[1]
            elif name == "stamina":
                stamina = values[0]
                effort = values[1]
            elif name == "speed":
                speed_amount = values[0]
                if len(values) >= 2:
                    speed_direction = values[1]
            elif name == "head_angle":
                neck_direction = values[0]
            else:
                pass

        return msg[0], msg[1], SenseBody(view_quality, view_width,
                                         stamina, effort,
                                         speed_amount, speed_direction,
                                         neck_direction)
    #
    # def _handle_change_player_type(self, msg):
    #     """
    #     Handle player change messages.
    #     """
    #
    # def _handle_player_param(self, msg):
    #     """
    #     Deals with player parameter information.
    #     """
    #
    # def _handle_player_type(self, msg):
    #     """
    #     Handles player type information.
    #     """
    #
    # def _handle_server_param(self, msg):
    #     """
    #     Stores server parameter information.
    #     """
    #
    #     # each list is two items: a value name and its value.  we add them all
    #     # to the ServerParameters class inside WorldModel programmatically.
    #     for param in msg[1:]:
    #         # put all [param, value] pairs into the server settings object
    #         # by setting the attribute programmatically.
    #         if len(param) != 2:
    #             continue
    #
    #         # the parameter and its value
    #         key = param[0]
    #         value = param[1]
    #
    #         # set the attribute if it was accounted for, otherwise alert the user
    #         if hasattr(self.wm.server_parameters, key):
    #             setattr(self.wm.server_parameters, key, value)
    #         else:
    #             raise AttributeError("Couldn't find a matching parameter in "
    #                                  "ServerParameters class: '%s'" % key)
    #
    # def _handle_init(self, msg):
    #     """
    #     Deals with initialization messages sent by the server.
    #     """
    #
    #     # set the player's uniform number, side, and the play mode as returned
    #     # by the server directly after connecting.
    #     side = msg[1]
    #     uniform_number = msg[2]
    #     play_mode = msg[3]
    #
    #     self.wm.side = side
    #     self.wm.uniform_number = uniform_number
    #     self.wm.play_mode = play_mode


if __name__ == "__main__":
    parser = MessageParser()

    msg_type, msg_time, objects = parser.parse((
        '(see 568 ((f l t) 30 -38 -0 0) ((f t l 20) 19.1 43 0 0) ((f t l 30) \
         18.7 12 -0 0) ((f t l 40) 23.3 -12 -0 0) ((f t l 50) 30.6 -27) \
         ((b) 1.2 5 -0.024 2.7) ((p "team_jason" 2) 0.7 -34 -0 0 42 42) \
         ((l t) 14.7 -64))'))

    print(objects)

    msg_type, msg_time, objects = parser.parse((
        '(sense_body 569 (view_mode high normal) (stamina 4000 1) (speed 0 -54) (head_angle 0) (kick 13) (dash 291) \
        (turn 135) (say 0) (turn_neck 0) (catch 0) (move 1) (change_view 0) (arm (movable 0) (expires 0) (target 0 0) \
        (count 0)) (focus (target none) (count 0)) (tackle (expires 0) (count 0)))'))

    print(objects)
