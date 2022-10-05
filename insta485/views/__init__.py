"""Views, one for each Insta485 page."""
from insta485.views.login import login, logout
from insta485.views.index import handle_like, handle_comment
from insta485.views.index import upload_file, show_index
from insta485.views.posts import create_post
from insta485.views.followers import show_followers
from insta485.views.explore import show_explore
from insta485.views.following import show_following
from insta485.views.delete import delete_page
from insta485.views.edit import edit_profile
from insta485.views.user import handle_follow_user, show_user, upload_img
from insta485.views.create import show_create, handle_account_ops
from insta485.views.password import change_password
