import nox


@nox.session
def blacken(session):
    session.install('black')
    if session.posargs and session.posargs[0] == 'check':
        session.run('black', '-S', '-v', '.', '--check')
    else:
        session.run('black', '-S', '-v', '.')


@nox.session
def lint(session):
    session.install('flake8')
    session.run('flake8', '-v', '.')


@nox.session(tags=['test'])
def coverage(session):
    session.install('.[test,render]')
    session.run('mkdir', '-p', 'data', external=True)
    session.run('pytest', '-vv', '-n', 'auto')
