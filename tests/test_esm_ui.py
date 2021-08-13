#!/usr/bin/env python

"""Tests for `esm_ui` package."""


import unittest
from click.testing import CliRunner

from esm_ui import esm_ui
from esm_ui import cli


class TestEsm_ui(unittest.TestCase):
    """Tests for `esm_ui` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'esm_ui.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
