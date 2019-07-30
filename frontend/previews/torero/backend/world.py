import base
import math
from collections import namedtuple

Toro = namedtuple(
    'Toro',
    ['rotation', 'load', 'x', 'y'])

Torero = namedtuple(
    'Torero', ['show_cape', 'x', 'y'])


def get_character(user, character):
    if user.type == base.TORO:
        return Toro(**character)
    elif user.type == base.TORERO:
        return Torero(**character)

    raise base.HandlerError(
        message='trying to handle_input of nonplayable character')


def handle_input(user, message):
    try:
        keys = message['keys']
    except KeyError:
        raise base.HandlerError(message='invalid input payload')

    try:
        character = get_character(user, message['character'])
    except TypeError:
        raise base.HandlerError(message='character payload misformed')
    except KeyError:
        raise base.HandlerError(message='invalid input payload')

    if user.type == base.TORO:
        return update_toro(keys, character)
    elif user.type == base.TORERO:
        return update_torero(keys, character)

    raise base.HandlerError(
        message='trying to handle_input of nonplayable character')


def update_torero(keys, torero):
    if not (keys['ArrowLeft'] or keys['ArrowRight']
            or keys['ArrowUp'] or keys['ArrowDown']) \
            and not (torero.show_cape or keys['Enter']):
        return

    newX = torero.x
    newY = torero.y

    if keys['ArrowLeft']:
        newX -= base.MOVE_INCREMENT
    if keys['ArrowRight']:
        newX += base.MOVE_INCREMENT
    if keys['ArrowUp']:
        newY -= base.MOVE_INCREMENT
    if keys['ArrowDown']:
        newY += base.MOVE_INCREMENT

    newX, newY = handle_bounds(newX, newY)
    return Torero(show_cape=keys['Enter'], x=newX, y=newY)


def update_toro(keys, toro):
    # rotation in degree to radians (unit for the length of an arc)
    if not (keys['KeyA'] or keys['KeyD'] or keys['Space']) \
       and toro.load <= 0:
        return

    newRotation = toro.rotation
    newLoad = 0
    theta = (toro.rotation + 90) * (math.pi/180)

    newThrusty = 0
    newThrustx = 0

    if not keys['Space'] and toro.load > 0:
        newThrusty = math.sin(theta) * toro.load \
            * base.THRUST_BY_LOAD_MULTIPLIER
        newThrustx = math.cos(theta) * toro.load \
            * base.THRUST_BY_LOAD_MULTIPLIER
        newLoad = max(toro.load - base.LOAD_COOLDOWN, 0)
    elif keys['Space']:
        newLoad = (toro.load + base.LOAD_INCREMENT) % 1

    if keys['KeyD']:
        newRotation += base.ROTATION_INCREMENT
    if keys['KeyA']:
        newRotation -= base.ROTATION_INCREMENT

    newX = toro.x + newThrustx
    newY = toro.y + newThrusty

    newX, newY = handle_bounds(newX, newY)
    return Toro(x=newX, y=newY, rotation=newRotation, load=newLoad)


def handle_bounds(x, y,
                  boundWidth=base.BOUNDS_WIDTH,
                  boundHeight=base.BOUNDS_HEIGHT):
    if x > boundWidth:
        newX = boundWidth
    elif x < 0:
        newX = 0
    else:
        newX = x

    if y > boundHeight:
        newY = boundHeight
    elif y < 0:
        newY = 0
    else:
        newY = y

    return newX, newY
