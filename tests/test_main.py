import pytest
import sys
from unittest.mock import patch
from core.command_parser import CommandParser
import main

def test_command_parser_initialization():
    parser = CommandParser()
    assert parser is not None
    assert parser.news_engine is not None
    assert parser.research_provider is not None

def test_command_parser_validation():
    parser = CommandParser()
    # Invalid symbol length
    res = parser.execute_command("AGENT2 UPDATE NEWS X")
    assert "REJECT: ENTITY_UNCERTAIN" in res
    
    # Unauthorized command
    res2 = parser.execute_command("AGENT4 UPDATE NEWS BBCA")
    assert "REJECT: Invalid agent" in res2
    
    # Web mode rejection for standalone Python execution
    res3 = parser.execute_command("AGENT2 UPDATE NEWS BBCA --MODE web")
    assert "REJECT: WEB mode is an IDE-assisted mode" in res3

def test_main_cli_execution_with_arguments(capsys):
    test_args = ["main.py", "AGENT2", "UPDATE", "NEWS", "X"]
    with patch.object(sys, 'argv', test_args):
        main.main()
        captured = capsys.readouterr()
        assert "AI SWING TRADING DESK - SEMI-MANUAL MODE" in captured.out
        assert "REJECT: ENTITY_UNCERTAIN" in captured.out
