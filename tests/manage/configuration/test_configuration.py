# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida.manage.configuration` module."""
import pytest

import aiida
from aiida.manage.manager import check_version


def test_check_version_release(monkeypatch, capsys, isolated_config):
    """Test that ``check_version`` prints nothing for a release version.

    If a warning is emitted, it should be printed to stdout. So even though it will go through the logging system, the
    logging configuration of AiiDA will interfere with that of pytest and the ultimately the output will simply be
    written to stdout, so we use the ``capsys`` fixture and not the ``caplog`` one.
    """
    version = '1.0.0'
    monkeypatch.setattr(aiida, '__version__', version)

    # Explicitly setting the default in case the test profile has it changed.
    isolated_config.set_option('warnings.development_version', True)

    check_version()
    captured = capsys.readouterr()
    assert not captured.err
    assert not captured.out


@pytest.mark.parametrize('suppress_warning', (True, False))
def test_check_version_development(monkeypatch, capsys, isolated_config, suppress_warning):
    """Test that ``check_version`` prints a warning for a post release development version.

    The warning can be suppressed by setting the option ``warnings.development_version`` to ``False``.

    If a warning is emitted, it should be printed to stdout. So even though it will go through the logging system, the
    logging configuration of AiiDA will interfere with that of pytest and the ultimately the output will simply be
    written to stdout, so we use the ``capsys`` fixture and not the ``caplog`` one.
    """
    version = '1.0.0.post0'
    monkeypatch.setattr(aiida, '__version__', version)

    isolated_config.set_option('warnings.development_version', not suppress_warning)

    check_version()
    captured = capsys.readouterr()
    assert not captured.err

    if suppress_warning:
        assert not captured.out
    else:
        assert f'You are currently using a post release development version of AiiDA: {version}' in captured.out
