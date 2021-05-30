
class SelectQueries:
    user_passwd = """
SELECT password_hash FROM homemanager.users WHERE username = %s
"""
    active_users = """
SELECT username_id FROM homemanager.user_statuses WHERE status = True
"""
    cameras = """
SELECT d.device_name, c.path_video, c.path_activation
FROM homemanager.cameras c INNER JOIN homemanager.devices d 
    on c.device_id = d.device_id
"""

    #identity_token = 'SELECT identity, token_id FROM tokens_t WHERE token = %s'
    #access = 'SELECT access_id, request_path, access_name FROM access_t'
    # access_tokens = """
    # SELECT
    #     t.identity
    # FROM
    #     access_tokens_t at
    #
    #     INNER JOIN tokens_t t
    #     on at.token_id = t.token_id
    # WHERE
    #     t.token = %s and at.access_id = %s
    # """
