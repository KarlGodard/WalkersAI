"""Views, one for each Insta485 page."""
from sketchy.views.login import login, logout, create_account, logged_in
from sketchy.views.index import show_index
from sketchy.views.favorites import favorites, chat
from sketchy.views.trivia import trivia_score
