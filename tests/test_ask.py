from types import SimpleNamespace
from unittest.mock import Mock, call

from app import ask as ask_module


def test_main_reuses_chat_for_followup_questions(monkeypatch, capsys):
    chat = Mock()
    chat.send_message.side_effect = [
        SimpleNamespace(text="first answer", usage_metadata=None),
        SimpleNamespace(text="follow-up answer", usage_metadata=None),
    ]
    client = Mock()
    client.chats.create.return_value = chat
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "first question"])
    questions = iter(["follow-up question", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask_module.main()

    client.chats.create.assert_called_once_with(model=ask_module.MODEL)
    assert chat.send_message.call_args_list == [
        call("first question"),
        call("follow-up question"),
    ]
    output = capsys.readouterr().out
    assert "first answer" in output
    assert "follow-up answer" in output