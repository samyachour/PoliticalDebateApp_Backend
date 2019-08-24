
minimum_password_length = 6
minimum_trigram_similarity = 0.09
maximum_debate_query = 100

content_type = "application/json"
v1_key = "v1"
post_key = "post"
version_key = "version"
data_key = "data"

# Request keys
pk_key = "pk"
debate_pk_key = "debate_pk"
point_pk_key = "point_pk"

message_key = "message"

debate_key = "debate"

debate_point_key = "debate_point"

search_string_key = "search_string"
all_progress_key = "all_progress"
all_starred_key = "all_starred"
filter_key = "filter"
last_updated_filter_value = "last_updated"
starred_filter_value = "starred"
progress_filter_value = "progress"
no_progress_filter_value = "no_progress"
random_filter_value = "random"
all_filters = [last_updated_filter_value, starred_filter_value, progress_filter_value, no_progress_filter_value, random_filter_value]

title_key = "title"
short_title_key = "short_title"
tags_key = "tags"
last_updated_key = "last_updated"
total_points_key = "total_points"
debate_map_key = "debate_map"

description_key = "description"
side_key = "side"
hyperlinks_key = "hyperlinks"
images_key = "images"
rebuttals_key = "rebuttals"

name_key = "name"
substring_key = "substring"
url_key = "url"
source_key = "source"

seen_points_key = "seen_points"
completed_percentage_key = "completed_percentage"
all_debate_points_key = "all_debate_points"

starred_list_key = "starred_list"
unstarred_list_key = "unstarred_list"

token_key = "token"
access_key = "access"
refresh_key = "refresh"

email_key = "email"
new_email_key = "new_email"

current_email_key = "current_email"
is_verified_key = "is_verified"

old_password_key = "old_password"
new_password_key = "new_password"
new_password_confirmation_key = "new_password_confirmation"
force_send_key = "force_send"
uidb64_key = "uidb64"

passwords_do_not_match_key = "passwords_do_not_match"
password_too_short_key = "passwords_too_short"

username_key = "username"
password_key = "password"

# URL names
filter_debates_name = "filter_debates"
get_debate_name = "get_debate"
get_progress_name = "get_progress"
get_all_post_progress_name = "get_all_post_progress"
post_progress_batch_name = "post_progress_batch"
starred_name = "starred"
auth_delete_name = "auth_delete"
auth_register_name = "auth_register"
auth_change_password_name = "auth_change_password"
auth_change_email_name = "auth_change_email"
auth_get_current_email_name = "auth_get_current_email"
auth_request_verification_link_name = "auth_request_verification_link"
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

# Success messages

success_response = "Success"

# Error messages
invalid_email_error = "Could not send, email is invalid."
invalid_link_error = "Link is invalid."

debate_get_error = "A debate ID is required."
debate_filter_invalid_search_string_error = "Invalid search string."
debate_filter_invalid_filter_format_error = "Invalid filter format."
debate_filter_unknown_filter_error = "Unknown filter."
debate_filter_missing_pk_array_error = "Used filter but didn't provide necessary associated array."
debate_filter_invalid_pk_array_format_error = "Your primary key array is not of the right format."
debate_filter_invalid_pk_array_items_format_error = "Your primary key array contains non-integer types."
progress_point_post_error = "Both debate ID and debate point ID are required to add a progress point."
progress_point_get_error = "A debate ID is required."
invalid_point_pk_error = "Could not find point associated with that ID."
progress_point_batch_post_error = "Incorrect format must be array of seen progress points."
starred_post_type_error = "Starred and unstarred values must be array types."
starred_post_empty_error = "No starred or unstarred data passed."
starred_post_format_error = "Arrays contain non-integer values."
password_length_error = "Password must be at least 6 characters."
register_post_error = "Both an email and a password are required to register a user."
change_password_post_error = "Both the old and new password are required to change user's password."
change_email_post_error = "A new email is required to change the user's email."
request_password_reset_post_error = "Need an email to request a password reset."
already_using_email_error = "User is already using this email."
