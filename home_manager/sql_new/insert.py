
class InsertQueries:
    user = """
INSERT INTO homemanager.users(username, passwd_hash) VALUES(%s, %s)
RETURNING user_id
"""
    device = """
INSERT INTO homemanager.devices(device_name, device_type) VALUES(%s, %s)
RETURNING device_id
"""
    token_session = """
INSERT INTO homemanager.tokens_session(token)
"""
    tokens = """
INSERT INTO homemanager.tokens(
    token_select, token_verify, token_renew, expires_in
) VALUES(%s, %s, %s, %s)
"""
    role = """
INSERT INTO homemanager.roles(
    role_name, path, method_get, method_post, method_put, method_delete
) VALUES(%s, %s, %s, %s, %s, %s)
"""
    camera = """
INSERT INTO homemanager.cameras(device_id, path_video, path_active) 
VALUES(%s, %s, %s)
"""
    motion = """
INSERT INTO homemanager.motions(motion_data, camera_id, motion_time) 
VALUES(%s, %s, %s)
"""
    user_status = """
INSERT INTO homemanager.user_statuses(user_id) VALUES(%s)
"""
    role_token = """
INSERT INTO homemanager.roles_tokens(role_id, token_id)
SELECT
    t.role_id, t.token_id
FROM
    homemanager.roles r,
    homemanager.tokens t
WHERE
    r.role_name = %s and t.token_select = %s
"""
