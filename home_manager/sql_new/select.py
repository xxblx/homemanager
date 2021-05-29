
class SelectQueries:
    user_passwd = 'SELECT passwd_hash FROM users_t WHERE username = %s'
    active_users = 'SELECT username_id FROM status_t WHERE status = True'
    identity_token = 'SELECT identity, token_id FROM tokens_t WHERE token = %s'
    access = 'SELECT access_id, request_path, access_name FROM access_t'
    cameras = 'SELECT camera_id, camera_file, camera_name, comment FROM video_t'

    access_tokens = """
    SELECT
        t.identity
    FROM
        access_tokens_t at

        INNER JOIN tokens_t t
        on at.token_id = t.token_id
    WHERE
        t.token = %s and at.access_id = %s
    """
