from multi_agents_game.chat_services.chat_server_fastapi import app
from multi_agents_game.config.server_config import (
    chat_service_base_port,
    num_chat_service_instances,
)


##################################################################################################################
def main() -> None:

    if num_chat_service_instances != 1:
        raise ValueError(
            "This script is only for running a single instance of the chat server."
        )

    import uvicorn

    uvicorn.run(app, host="localhost", port=chat_service_base_port)


##################################################################################################################

if __name__ == "__main__":
    main()

##################################################################################################################
