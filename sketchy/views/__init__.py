"""Views, one for each Insta485 page."""
from sketchy.views.login import login, logout
from sketchy.views.index import handle_like, handle_comment
from sketchy.views.index import upload_file, show_index
from sketchy.views.posts import create_post
from sketchy.views.followers import show_followers
from sketchy.views.explore import show_explore
from sketchy.views.following import show_following
from sketchy.views.delete import delete_page
from sketchy.views.edit import edit_profile
from sketchy.views.user import handle_follow_user, show_user, upload_img
from sketchy.views.create import show_create, handle_account_ops
from sketchy.views.password import change_password
