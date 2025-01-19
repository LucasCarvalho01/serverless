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
USER_CODE_BASE64 = os.getenv("USER_CODE_BASE64", "")
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
                
                execute_dynamic_function(current_value, dict(current_value), context)
            
            time.sleep(int(REDIS_MONITORING_PERIOD_SECONDS))
        
        except redis.ConnectionError as e:
            print(f"Redis connection error: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
