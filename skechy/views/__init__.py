"""Views, one for each Insta485 page."""
from skechy.views.login import login, logout
from skechy.views.index import handle_like, handle_comment
from skechy.views.index import upload_file, show_index
from skechy.views.posts import create_post
from skechy.views.followers import show_followers
from skechy.views.explore import show_explore
from skechy.views.following import show_following
from skechy.views.delete import delete_page
from skechy.views.edit import edit_profile
from skechy.views.user import handle_follow_user, show_user, upload_img
from skechy.views.create import show_create, handle_account_ops
from skechy.views.password import change_password
