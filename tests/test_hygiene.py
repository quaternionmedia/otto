"""Importing otto does nothing but import, and the API lists real templates."""

import importlib
import os
import sys

from fastapi.testclient import TestClient

from otto import templates
from otto.main import app


def test_the_template_list_is_the_registry():
    names = TestClient(app).get('/templates').json()

    assert names == list(templates.TEMPLATES)
    assert 'textBox' in names and 'makeColor' in names
    for helper in ('concatenate_videoclips', 'ct', 'defaults', 'rgbToDec'):
        assert helper not in names


def test_importing_cliparse_does_not_read_the_command_line(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['some-other-program', '--not-ottos-flag'])
    sys.modules.pop('otto.cliparse', None)

    cliparse = importlib.import_module('otto.cliparse')

    assert cliparse.parse_args(['--dry', '-s', '320', '240']).size == [320, 240]


def test_importing_log_creates_nothing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    sys.modules.pop('otto.log', None)

    log = importlib.import_module('otto.log')

    assert os.listdir(tmp_path) == []
    logger = log.configure(str(tmp_path / 'logs'))
    try:
        assert len(os.listdir(tmp_path / 'logs')) == 1
    finally:
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)
