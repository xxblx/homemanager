
class UpdateQueries:
    user_status = """
UPDATE homemanager.user_statuses SET status = %s WHERE user_id = %s
"""
