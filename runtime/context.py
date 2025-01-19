import datetime
from typing import Dict, Any

class Context:
    def __init__(
        self,
        host: str,
        port: int,
        input_key: str,
        output_key: str,
        function_getmtime: str,
        last_execution: str,
        env: Dict[str, Any] = None,
    ):
        self.host = host
        self.port = port
        self.input_key = input_key
        self.output_key = output_key
        self.function_getmtime = function_getmtime
        self.last_execution = last_execution
        self.env = env
