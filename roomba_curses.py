""" Roomba simulation curses"""
import argparse
import curses
from random import randint
from random import choice
from time import sleep

from typing import List
from typing import Tuple

ROOMBA = "@"
DUST1 = "."
DUST2 = ":"
DUST3 = "&"
BASE = "["
OPPOSITE_DIRECTION = {"N": "S", "NE": "SW", "E": "W", "SE": "NW",
                      "S": "N", "SW": "NE", "W": "E", "NW": "SE"}


class RoombaError(Exception):
    pass


class Roomba:
    def __init__(self, base_y: int, base_x: int,
                 width: int, height: int, options: dict) -> None:
        self.base_y = base_y
        self.base_x = base_x
        self.y = base_y
        self.x = base_x + 1
        self.room_width = width - 1
        self.room_height = height - 3
        self.charge = options["battery_size"]
        self.recharge_rate = options["recharge_rate"]
        self.discharge_rate = options["discharge_rate"]
        self.battery_size = options["battery_size"]
        if self.room_height > self.room_width:
            self.low_charge = self.room_height * self.discharge_rate
        else:
            self.low_charge = self.room_width * self.discharge_rate
        self.state = "Ready"  # ready, cleaning, charging
        self.speed = options["speed"]
        self.speed_count = 0
        self.model = options["model"]
        self.previous_positions = [(self.y, self.x)]
        self.direction = ""
        self.reverse_direction = ""

    def operate(self, room: list) -> bool:
        # checks the state do _move or _recharge
        if self.state == "Ready" or self.state == "Cleaning":
            if self.charge <= 0:
                return True
            elif self.speed_count == self.speed:
                self.speed_count = 0
                self.charge -= self.discharge_rate
                room[self.y][self.x] = " "
                self._move()
                room[self.y][self.x] = ROOMBA
                return False
            else:
                room[self.y][self.x] = ROOMBA
                self.speed_count += 1
                return False
        elif self.state == "Charging":
            self._charging()
            return False

    def get_statues(self) -> Tuple[float, str]:
        # returns the battery percent and state
        return (self.charge / self.battery_size) * 100, self.state

    def _move(self) -> None:
        if self.charge <= self.low_charge:
            self._return_home()
        elif self.model == 1:
            self._move1()
        elif self.model == 2:
            self._move2()
        elif self.model == 3:
            self._move3()

    def _move1(self) -> None:
        self.state = "Cleaning"
        directions = []
        if self.y > 0:
            if self.y - 1 != self.base_y and self.x != self.base_x:
                directions.append((self.y - 1, self.x))

        if self.y > 0 and self.x < self.room_width:
            if self.y - 1 != self.base_y and self.x + 1 != self.base_x:
                directions.append((self.y - 1, self.x + 1))

        if self.x < self.room_width:
            if self.x + 1 != self.base_x and self.y != self.base_y:
                directions.append((self.y, self.x + 1))

        if self.x < self.room_width and self.y < self.room_height:
            if self.x + 1 != self.base_x and self.y + 1 != self.base_y:
                directions.append((self.y + 1, self.x + 1))

        if self.y < self.room_height:
            if self.y + 1 != self.base_y and self.x != self.base_x:
                directions.append((self.y + 1, self.x))

        if self.y < self.room_height and self.x > 0:
            if self.y + 1 == self.base_y and self.x - 1 == self.base_x:
                pass
            else:
                directions.append((self.y + 1, self.x - 1))

        if self.x > 0:
            if self.x - 1 == self.base_x and self.y == self.base_y:
                pass
            else:
                directions.append((self.y, self.x - 1))

        if self.x > 0 and self.y > 0:
            if self.y - 1 == self.base_y and self.x - 1 == self.base_x:
                pass
            else:
                directions.append((self.y - 1, self.x - 1))

        self.y, self.x = choice(directions)

    def _move2(self) -> None:
        self.state = "Cleaning"
        directions = []
        if self.y > 0:
            if self.y - 1 == self.base_y and self.x == self.base_x:
                pass
            elif (self.y - 1, self.x) in self.previous_positions:
                pass
            else:
                directions.append((self.y - 1, self.x))

        if self.y > 0 and self.x < self.room_width:
            if self.y - 1 == self.base_y and self.x + 1 == self.base_x:
                pass
            elif (self.y - 1, self.x + 1) in self.previous_positions:
                pass
            else:
                directions.append((self.y - 1, self.x + 1))

        if self.x < self.room_width:
            if self.x + 1 == self.base_x and self.y == self.base_y:
                pass
            elif (self.y, self.x + 1) in self.previous_positions:
                pass
            else:
                directions.append((self.y, self.x + 1))

        if self.x < self.room_width and self.y < self.room_height:
            if self.x + 1 == self.base_x and self.y + 1 == self.base_y:
                pass
            elif (self.y + 1, self.x + 1) in self.previous_positions:
                pass
            else:
                directions.append((self.y + 1, self.x + 1))

        if self.y < self.room_height:
            if self.y + 1 == self.base_y and self.x == self.base_x:
                pass
            elif (self.y + 1, self.x) in self.previous_positions:
                pass
            else:
                directions.append((self.y + 1, self.x))

        if self.y < self.room_height and self.x > 0:
            if self.y + 1 == self.base_y and self.x - 1 == self.base_x:
                pass
            elif (self.y + 1, self.x - 1) in self.previous_positions:
                pass
            else:
                directions.append((self.y + 1, self.x - 1))

        if self.x > 0:
            if self.x - 1 == self.base_x and self.y == self.base_y:
                pass
            elif (self.y, self.x + 1) in self.previous_positions:
                pass
            else:
                directions.append((self.y, self.x - 1))

        if self.x > 0 and self.y > 0:
            if self.y - 1 == self.base_y and self.x - 1 == self.base_x:
                pass
            elif (self.y - 1, self.x - 1) in self.previous_positions:
                pass
            else:
                directions.append((self.y - 1, self.x - 1))

        self.y, self.x = choice(directions)
        self.previous_positions.append((self.y, self.x))
        if len(self.previous_positions) > 4:
            self.previous_positions.pop(0)

    def _move3(self) -> None:
        good_directions = self._check_directions()
        if self.direction == "" or self.direction not in good_directions:
            self.direction = choice(good_directions)
            self.reverse_direction = OPPOSITE_DIRECTION[self.direction]
        if self.direction == "N":
            self.y -= 1
        elif self.direction == "NE":
            self.y -= 1
            self.x += 1
        elif self.direction == "E":
            self.x += 1
        elif self.direction == "SE":
            self.y += 1
            self.x += 1
        elif self.direction == "S":
            self.y += 1
        elif self.direction == "SW":
            self.y += 1
            self.x -= 1
        elif self.direction == "W":
            self.x -= 1
        elif self.direction == "W":
            self.x -= 1
        elif self.direction == "NW":
            self.y -= 1
            self.x -= 1

    def _return_home(self) -> Tuple[int, int]:
        if self.y > self.base_y:
            y = self.y - 1
        elif self.y < self.base_y:
            y = self.y + 1
        else:
            y = self.y
        if self.x > self.base_x + 1:
            x = self.x - 1
        elif self.x < self.base_x + 1:
            x = self.x + 1
        else:
            x = self.x
        if x == self.base_x + 1 and y == self.base_y:
            self.state = "Charging"
        self.y = y
        self.x = x
        return self.y, self.x

    def _check_directions(self) -> List[str]:
        good_directions = []
        if self.y - 1 >= 0:  # N
            if self.y - 1 == self.base_y and self.x == self.base_x:
                pass
            else:
                good_directions.append("N")
        if self.y - 1 >= 0 and self.x + 1 < self.room_width:
            if self.y - 1 == self.base_y and self.x + 1 == self.base_x:
                pass
            else:
                good_directions.append("NE")
        if self.x + 1 < self.room_width:
            if self.y == self.base_y and self.x + 1 == self.base_x:
                pass
            else:
                good_directions.append("E")
        if self.y + 1 <= self.room_height and self.x + 1 < self.room_width:
            if self.y + 1 == self.base_y and self.x + 1 == self.base_x:
                pass
            else:
                good_directions.append("SE")
        if self.y + 1 <= self.room_height:
            if self.y + 1 == self.base_y and self.x == self.base_x:
                pass
            else:
                good_directions.append("S")
        if self.y + 1 <= self.room_height and self.x - 1 >= 0:
            if self.y + 1 == self.base_y and self.x - 1 == self.base_x:
                pass
            else:
                good_directions.append("SW")
        if self.x - 1 >= 0:
            if self.y == self.base_y and self.x - 1 == self.base_x:
                pass
            else:
                good_directions.append("W")
        if self.y - 1 >= 0 and self.x - 1 >= 0:
            if self.y - 1 == self.base_y and self.x - 1 == self.base_x:
                pass
            else:
                good_directions.append("NW")
        if self.reverse_direction in good_directions:
            good_directions.pop(good_directions.index(self.reverse_direction))
        return good_directions

    def _charging(self) -> None:
        self.charge += self.recharge_rate
        if self.charge >= self.battery_size:
            self.charge = self.battery_size
            self.state = "Ready"


def add_dust(room: list, height: int, width: int) -> None:
    if randint(1, 3) <= 2:
        random_y = randint(0, height - 3)
        random_x = randint(0, width - 2)
        if room[random_y][random_x] == BASE:
            pass
        elif room[random_y][random_x] == ROOMBA:
            pass
        else:
            if room[random_y][random_x] == " ":
                room[random_y][random_x] = DUST1
            elif room[random_y][random_x] == DUST1:
                room[random_y][random_x] = DUST2
            elif room[random_y][random_x] == DUST2:
                room[random_y][random_x] = DUST3


def setup_room_list(width: int, height: int) -> list:
    return [[" " for _ in range(width - 1)] for _ in range(height - 2)]


def roomba_option(model_number: int) -> dict:
    options = {}
    if model_number == 1:
        options["model"] = 1
        options["battery_size"] = 400
        options["recharge_rate"] = 5
        options["discharge_rate"] = 2
        options["speed"] = 4
    if model_number == 2:
        options["model"] = 2
        options["battery_size"] = 500
        options["recharge_rate"] = 6
        options["discharge_rate"] = 2
        options["speed"] = 3
    elif model_number == 3:
        options["model"] = 3
        options["battery_size"] = 600
        options["recharge_rate"] = 6
        options["discharge_rate"] = 1.5
        options["speed"] = 2
    return options


def curses_main(screen, model: int) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    # curses.init_pair()
    height, width = screen.getmaxyx()
    if height <= 15 or width <= 15:
        raise RoombaError("Error window size should be greater than 15")
    room = setup_room_list(width, height)
    roomba = Roomba(5, 0, width, height, roomba_option(model))
    room[5][0] = BASE
    reset = False
    running = True
    while running:
        resize = curses.is_term_resized(height, width)
        if resize or reset:
            height, width = screen.getmaxyx()
            if height <= 15 or width <= 15:
                raise RoombaError("Error window size should be greater than 15")
            room = setup_room_list(width, height)
            roomba = Roomba(5, 0, width, height, roomba_option(model))
            room[5][0] = BASE
        screen.clear()
        add_dust(room, height, width)
        reset = roomba.operate(room)
        for y, row in enumerate(room):
            for x, d in enumerate(row):
                if d == ROOMBA:
                    screen.addstr(y, x, d, curses.A_BOLD)
                else:
                    screen.addstr(y, x, d)
        battery, state = roomba.get_statues()
        msg = f" Model: {model}  Battery: {battery:.1f}%   {state}"
        screen.addstr(height - 1, 0, msg, curses.A_BOLD)
        screen.refresh()
        ch = screen.getch()
        if ch in [81, 113]:
            running = False
        sleep(0.25)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", dest="model",
                        type=int,
                        choices=[1, 2, 3],
                        default=1,
                        help="Model number to use")
    args = parser.parse_args()
    try:
        curses.wrapper(curses_main, args.model)
    except RoombaError as e:
        print(e)
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit(main())
