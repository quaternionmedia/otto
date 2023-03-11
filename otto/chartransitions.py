import numpy as np


def rotMatrix(a):
    return np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])


def damping(t):
    return 1.0 / (0.3 + t**8)


def vortex(screenpos, i, nletters):
    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos + 400 * damping(t) * rotMatrix(0.5 * damping(t) * a).dot(
        v
    )


def cascade(screenpos, i):
    v = np.array([0, -1])

    def d(t):
        return 1 if t < 0 else abs(np.sinc(t) / (1 + t**4))

    return lambda t: screenpos + v * 400 * d(t - 0.15 * i)


def arrive(screenpos, i):
    v = np.array([-1, 0])

    def d(t):
        return max(0, 3 - 3 * t)

    return lambda t: screenpos - 400 * v * d(t - 0.2 * i)


def vortexout(screenpos, i, nletters):
    def d(t):
        # damping
        return max(0, t)

    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(
        v
    )


def moveLetters(letters, funcpos):
    return [
        letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
        for i, letter in enumerate(letters)
    ]
