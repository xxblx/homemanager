
class UpdateQueries:
    user_status = """
UPDATE homemanager.user_statuses SET status = %s WHERE user_id = %s
"""
    camera_settings = """
UPDATE homemanager.cameras 
SET stream = %s, motion_detection = %s, night_mode = %s
WHERE device_id = %s
"""
