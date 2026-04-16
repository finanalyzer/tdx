from openbb_core.app.service.user_service import UserService

def test_get_user_settings(logger):
    user_setting = UserService.read_from_file()
    assert user_setting is not None

