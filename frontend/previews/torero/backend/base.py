import logging
import os

DEBUG = os.environ.get('DEBUG', True)

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT,
                    level=logging.DEBUG if DEBUG else logging.INFO)
MAIN_LOGGER = logging.getLogger('main')
# TODO enum
TORO = 'TORO'
TORERO = 'TORERO'
PLAYABLE_USER_TYPES = {TORO, TORERO}
NONPLAYABLE_USER_TYPES = {'SPECTATOR', }
USER_TYPES = (*NONPLAYABLE_USER_TYPES, *PLAYABLE_USER_TYPES)
THRUST_BY_LOAD_MULTIPLIER = 70
MOVE_INCREMENT = 4
ROTATION_INCREMENT = 5
LOAD_COOLDOWN = .05
LOAD_INCREMENT = .01
BOUNDS_HEIGHT = 400 - 40
BOUNDS_WIDTH = 400 - 40


class HandlerError(Exception):
    def __init__(self, message=None):
        self.message = message or self.MESSAGE
        assert self.message

    def serialize(self):
        return dict(type='error', msg=self.message)


class UserNotInRoom(HandlerError):
    MESSAGE = 'user not in room'


class RoomInactive(HandlerError):
    MESSAGE = 'room is not active'
