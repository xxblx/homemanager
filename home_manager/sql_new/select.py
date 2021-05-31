
class SelectQueries:
    user_passwd = """
SELECT password_hash FROM homemanager.users WHERE username = %s
"""
    active_users = """
SELECT user_id FROM homemanager.user_statuses WHERE status = True
"""
    cameras = """
SELECT d.device_name, c.path_video, c.path_activation
FROM homemanager.cameras c INNER JOIN homemanager.devices d 
    on c.device_id = d.device_id
"""
    camera_settings = """
SELECT path_activation, stream, motion_detection, night_mode
FROM homemanager.cameras WHERE device_id = %s
"""
    token_auth = """
SELECT
    d.device_id, d.device_name, t.token_verify
FROM
    homemanager.tokens t INNER JOIN homemanager.devices d 
    on t.device_id = d.device_id
WHERE
    t.token_select = %s and (t.expires_in >= now() or t.expires_in is NULL)
"""
    token_session = """
SELECT device_id, permanent_requested
FROM homemanager.tokens_session WHERE expires_in >= now()
"""
    device_role = """
SELECT
    r.role_name
FROM
    homemanager.roles_devices rd 
    INNER JOIN homemanager.roles_paths rp on rd.role_id = rp.role_id
    INNER JOIN homemanager.roles r on rd.role_id = r.role_id
WHERE
    rd.device_id = %s and path = %s and {method_col} = True
"""
