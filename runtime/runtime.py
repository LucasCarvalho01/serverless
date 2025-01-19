import os
import time
import redis
import json
import importlib.util
import tempfile
import zipfile
import datetime
import pytz
from pathlib import Path
import base64
from context import Context

REDIS_IP = os.getenv("REDIS_IP", "0.0.0.0")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_INPUT_KEY = os.getenv("REDIS_INPUT_KEY", "metrics")
REDIS_OUTPUT_KEY = os.getenv("REDIS_OUTPUT_KEY", "lucascarvalho-proj3-output")
REDIS_MONITORING_PERIOD_SECONDS = os.getenv("REDIS_MONITORING_PERIOD_SECONDS", "5")
USER_CODE_BASE64 = os.getenv("USER_CODE_BASE64", "UEsDBBQACAAIAGK5MloAAAAAAAAAAAAAAAAKACAAaGFuZGxlci5weXV4CwABBAAAAAAEAAAAAFVUDQAHOF+MZ8WMjWc4X4xnjVRNi9swEL0b/B+ETnYae7M99BDIXhYKhdJCr0sQjjx2tJElVx/uhpD/3vFXq5gsrU6W5r2Z92Yki6bVxpFXq1UciXEjdV0LVcdRZXRDuJYSuBNaWTIBSvjpIY7iaELmh8IK/qxVJepEQgdyN0e+fPv8PR2BYMhuzp3X4L4OZwljqmiAsbRPWEJFjoUqJQaEar3bklJwt0YVysEbbvXhFdWkJHsaIts4Irh469lRWKfNGYtM4BxU1xdKaBCma3K5DrV6XqUNOcGZCEWGcjlubJJOWfslKjLQWzAclMtoj0VUAJlgfR6lXR8P6i1wC7EvSNqj4qGjSVO8SVC7x4/pLWlJyIu2BVWOHRpO/hgqupohHFNe/uaoKB5n3gmZXU7X7NPGAqdbYn2TdCl5IFgUPwJ835U16RZWcuGgwe6MwOtccuoMU+B+aXNiUBuwFhUkQRcHpRQhTGjGtccBGcvAHTfZ4ezAMosp6J48BM6T/2Z9CPv1b5YB3tF9SlbkcbMZqenSTQMNWma84Ee49ZLMujphnC/kBM0GaPmOmgX24KsKRfUiQsf3wU67Qr6nF3vtpbudN50v6zSSbBwJjvz+rNZ3qKGpgBi2JaCtVtPFW9yN4CW+3LzC/tIH+xk//idyoSqdVPTH4K0o9ZZcRp9XGhh33qjJfxz9BlBLBwg/jVgR+QEAAMkEAABQSwECFAMUAAgACABiuTJaP41YEfkBAADJBAAACgAYAAAAAAAAAAAAtoEAAAAAaGFuZGxlci5weXV4CwABBAAAAAAEAAAAAFVUBQABOF+MZ1BLBQYAAAAAAQABAFAAAABRAgAAAAA=")
USER_ENTRYPOINT_FUNCTION = os.getenv("USER_ENTRYPOINT_FUNCTION", "handler")

usercode_last_update = None

redis_client = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, decode_responses=True)

def get_redis_data():
    data = redis_client.get(REDIS_INPUT_KEY)
    if data:
        return json.loads(data)
    return {}

def decode_zip_from_base64(base64_content, target_dir):
    zip_path = Path(target_dir) / "code.zip"
    with open(zip_path, "wb") as f:
        f.write(base64.b64decode(base64_content))
    return zip_path

def load_pyfile():
    with open("/opt/usermodule.py", "r") as f:
        module_name = f.stem
        spec = importlib.util.spec_from_file_location(module_name, f)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

def load_all_modules_from_dir(directory):
    modules = {}
    for py_file in Path(directory).glob("**/*.py"):
        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[module_name] = module
    return modules

def find_function_in_modules(modules):
    for module_name, module in modules.items():
        if hasattr(module, USER_ENTRYPOINT_FUNCTION):
            return getattr(module, USER_ENTRYPOINT_FUNCTION)
    raise ValueError(f"Function '{USER_ENTRYPOINT_FUNCTION}' not found in any loaded module.")

def extract_zip(zip_path, target_dir):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)

def execute_dynamic_function(input, context):
    global usercode_last_update

    if not USER_CODE_BASE64:
        raise ValueError("USER_CODE_BASE64 environment variable is not set or is empty.")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = decode_zip_from_base64(USER_CODE_BASE64, temp_dir)
        load_pyfile()
        extract_zip(zip_path, temp_dir)
        usercode_last_update = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')
        modules = load_all_modules_from_dir(temp_dir)
        func = find_function_in_modules(modules)
        func(input, context)

def main():
    last_timestamp = None
    env = {}
    
    while True:
        try:
            current_value = get_redis_data()

            current_timestamp = current_value.get("timestamp")
                                      
            if current_timestamp != last_timestamp:
                print(f"Value changed: {current_timestamp}")
                
                last_timestamp = current_timestamp

                context = Context(REDIS_IP, REDIS_PORT, REDIS_INPUT_KEY, REDIS_OUTPUT_KEY, usercode_last_update, last_timestamp, env)
                
                execute_dynamic_function(dict(current_value), context)
            
            time.sleep(int(REDIS_MONITORING_PERIOD_SECONDS))
        
        except redis.ConnectionError as e:
            print(f"Redis connection error: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
