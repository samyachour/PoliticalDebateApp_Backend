
minimum_password_length = 6
minimum_trigram_similarity = 0.1

# Request keys
pk_key = "pk"

debate_point_key = "debate_point"

completed_key = "completed"

token_key = "token"

email_key = "email"

new_email_key = "new_email"

old_password_key = "old_password"
new_password_key = "new_password"

force_send_key = "force_send"

uidb64_key = "uidb64"

message_key = "message"

starred_list_key = "starred_list"
unstarred_list_key = "unstarred_list"

access_key = "access"

refresh_key = "refresh"

debate_key = "debate"

seen_points_key = "seen_points"

post_key = "post"

v1_key = "v1"

version_key = "version"

data_key = "data"

title_key = "title"

last_updated_key = "last_updated"

total_points_key = "total_points"

debate_map_key = "debate_map"

username_key = "username"
password_key = "password"

content_type = "application/json"

new_password_confirmation_key = "new_password_confirmation"

search_string_key = "search_string"

# URL names
search_debates_name = "search_debates"
get_debate_name = "get_debate"
get_progress_name = "get_progress"
get_all_progress_name = "get_all_progress"
post_progress_name = "post_progress"
starred_name = "starred"
auth_delete_name = "auth_delete"
auth_register_name = "auth_register"
auth_change_password_name = "auth_change_password"
auth_change_email_name = "auth_change_email"
auth_token_obtain_name = "auth_token_obtain"
auth_token_refresh_name = "auth_token_refresh"
auth_password_reset_form_name = "auth_password_reset_form"
auth_password_reset_submit_name = "auth_password_reset_submit"
auth_request_password_reset_name = "auth_request_password_reset"
auth_verify_name = "auth_verify"

# URL Parts
auth_string = "auth"
password_reset_form_string = "password-reset-form"
password_reset_submit_string = "password-reset-submit"
verify_string = "verify"

# Error messages
progress_point_post_error = "Both debate ID and debate point are required to add a progress point"
debate_get_error = "A debate ID is required"
progress_point_get_error = "A debate ID is required"
starred_post_type_error = "Starred and unstarred values must be array types"
starred_post_empty_error = "No starred or unstarred data passed"
starred_post_format_error = "Arrays contain non-integer values"
password_length_error = "Password must be at least 6 characters"
register_post_error = "Both an email and a password are required to register a user"
change_password_post_error = "Both the old and new password are required to change user's password"
change_email_post_error = "A new email is required to change the user's email"
request_password_reset_post_error = "Need an email to request a password reset"
