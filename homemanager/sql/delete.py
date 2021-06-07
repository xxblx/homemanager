
class DeleteQueries:
    token_session = 'DELETE FROM homemanager.tokens_session WHERE token = %s'
    device_name = 'DELETE FROM homemanager.devices WHERE device_name = %s'
