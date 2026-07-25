from copy import deepcopy
from pprint import pprint
from .levels import Levels, levels


class Board:
    def __init__(self, level_name):
        self.level = Levels(level_name)

    def __str__(self):
        pprint(self.level.layout)
        return ""

    def __repr__(self):
        self.__str__()
        return ""

    def __eq__(self, other):
        if not isinstance(other, Board):
            return False
        return tuple(map(tuple, self.level.layout)) == tuple(map(tuple, other.level.layout))

    def __hash__(self):
        lst = [tuple(map(tuple, self.level.layout))]
        if self.level.button is not None:
            for button in self.level.button.keys():
                lst.append(self.level.button[button][0])

        return hash(tuple(lst))

    def is_goal(self, position):
        return self.level.is_goal(position)

    def is_inside(self, position):
        """Return True when a board coordinate is inside the level matrix."""
        x, y = position
        return 0 <= x < self.level.height and 0 <= y < self.level.width

    def is_fatal(self, block):
        pos1, pos2 = (block.x1, block.y1), (block.x2, block.y2)
        position = (pos1, pos2)
        tiles_list = list(map(self.level.get_tiletype, position))
        if "VOID" in tiles_list:
            return True
        elif "HIDDEN_PATH" in tiles_list:
            path_positions = []

            if "HIDDEN_PATH" == tiles_list[0]:
                path_positions.append(pos1)
            if "HIDDEN_PATH" == tiles_list[1]:
                path_positions.append(pos2)

            # A malformed level should not crash the game merely because a
            # hidden-path tile has no button entry.
            if not self.level.button:
                return True

            for button in self.level.button.keys():
                for path in path_positions:
                    if path in self.level.button[button][1]:
                        if not self.level.button[button][0]:
                            return True
        elif block.orientation == "upright" and tiles_list.count("GLASS_FLOOR") == 2:
            return True
        return False

    def refresh_layout(self, block):
        self.level.layout = deepcopy(levels[self.level.level_name]["layout"])
        pos1, pos2 = (block.x1, block.y1), (block.x2, block.y2)
        position = (pos1, pos2)
        tiles_list = list(map(self.level.get_tiletype, position))

        if self.level.button:
            if tiles_list.count("BUTTON_TYPE_X") == 2:
                self.level.button[pos1][0] = not self.level.button[pos1][0]
            elif tiles_list.count("BUTTON_TYPE_HEX") >= 1:
                try:
                    self.level.button[pos1][0] = not self.level.button[pos1][0]
                except KeyError:
                    self.level.button[pos2][0] = not self.level.button[pos2][0]
            elif tiles_list.count("BUTTON_ONE_TIME_USE") == 2:
                try:
                    self.level.button[pos1][0] = False
                except KeyError:
                    self.level.button[pos2][0] = False

            for button in self.level.button.keys():
                for hidden_path_coordinate in self.level.button[button][1]:
                    x, y = hidden_path_coordinate
                    if self.level.button[button][0]:
                        self.level.layout[x][y] = 0
                    else:
                        self.level.layout[x][y] = -1

        # Manual play calls refresh_layout before checking the lose condition.
        # Guard every write so negative indices do not wrap around and positive
        # out-of-range indices do not raise IndexError after a falling move.
        pos1 = (block.x1, block.y1)
        pos2 = (block.x2, block.y2)
        if block.orientation == "upright":
            if self.is_inside(pos1):
                self.level.layout[block.x1][block.y1] = 1
        else:
            if self.is_inside(pos1):
                self.level.layout[block.x1][block.y1] = 2
            if self.is_inside(pos2):
                self.level.layout[block.x2][block.y2] = 2

        return self.level.layout

    def switch_level(self):
        next_level = self.level.switch_level()
        self.level = Levels(next_level)