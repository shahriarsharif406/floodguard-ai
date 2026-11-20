import os
import pytest
from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(__file__))
PAGES = ["1_command_center", "2_submit_report", "3_report_detail", "4_moderator", "5_analytics",
         "6_situation_report", "7_about_limits"]


def _at(page, mode="Replay 2022"):
    at = AppTest.from_file(f"{ROOT}/pages/{page}.py", default_timeout=60)
    at.session_state["mode_label"] = mode
    at.session_state["replay_date"] = "2022-06-20"
    at.session_state["live_calls"] = 0
    at.session_state["submit_times"] = []
    at.session_state["playing"] = False
    at.session_state["detail_id"] = 3
    return at


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_replay(page):
    at = _at(page).run()
    assert not at.exception


@pytest.mark.parametrize("page", ["1_command_center", "5_analytics", "6_situation_report"])
def test_page_renders_live(page):
    at = _at(page, "Live (today)").run()
    assert not at.exception


def test_switch_to_replay_button():
    at = _at("1_command_center", "Live (today)").run()
    at.button[0].click().run()
    assert not at.exception
