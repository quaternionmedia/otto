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
    # The project moved from flake8 to ruff, but this session did not, so it
    # checked the code with a linter nothing else used. The rules ruff applies
    # are in pyproject.toml.
    session.install('ruff')
    session.run('ruff', 'check', '.')


@nox.session(tags=['test'])
def coverage(session):
    # See build-constraints.txt: bezier cannot be built with setuptools 81+.
    constraints = 'build-constraints.txt'
    session.install(
        '.[test,render]',
        env={'PIP_BUILD_CONSTRAINT': constraints, 'PIP_CONSTRAINT': constraints},
    )
    session.run('mkdir', '-p', 'data', external=True)
    session.run('pytest', '-vv', '-n', 'auto')
