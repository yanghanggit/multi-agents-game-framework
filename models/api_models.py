from pydantic import BaseModel


################################################################################################################
################################################################################################################
################################################################################################################
class APIEndpointConfigurationRequest(BaseModel):
    pass


class APIEndpointConfiguration(BaseModel):
    TEST_URL: str = ""
    LOGIN_URL: str = ""
    LOGOUT_URL: str = ""
    START_URL: str = ""
    HOME_RUN_URL: str = ""


class APIEndpointConfigurationResponse(BaseModel):
    content: str = ""
    api_endpoints: APIEndpointConfiguration = APIEndpointConfiguration()
    error: int = 0
    message: str = ""


################################################################################################################
################################################################################################################
################################################################################################################


class LoginRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""


class LoginResponse(BaseModel):
    actor: str = ""
    error: int = 0
    message: str = ""


################################################################################################################
################################################################################################################
################################################################################################################


class LogoutRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""


class LogoutResponse(BaseModel):
    error: int = 0
    message: str = ""


################################################################################################################
################################################################################################################
################################################################################################################
class StartRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class StartResponse(BaseModel):
    error: int = 0
    message: str = ""


################################################################################################################
################################################################################################################
################################################################################################################


class HomeRunRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    user_input: str = ""


class HomeRunResponse(BaseModel):
    error: int = 0
    message: str = ""


################################################################################################################
################################################################################################################
################################################################################################################
