import os
import time
import redis
import json

REDIS_IP = os.getenv('REDIS_IP', '0.0.0.0')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', 'metrics')
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', 'lucascarvalho-proj3-output')
REDIS_MONITORING_PERIOD_SECONDS = os.getenv('REDIS_MONITORING_PERIOD_SECONDS', '5')
USER_CODE = os.getenv('USER_CODE', '')

redis_client = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, decode_responses=True)

def get_redis_data():
    data = redis_client.get(REDIS_INPUT_KEY)
    if data:
        return json.loads(data)
    return {}

def execute_code(code, input, context):
    try:
        exec(code)

        handler(input, context)
    except Exception as e:
        print(f"Error executing code: {e}")

def main():
    last_timestamp = None
    
    while True:
        try:
            current_value = get_redis_data()

            current_timestamp = current_value.get("timestamp")
                                        
            if current_timestamp != last_timestamp:
                print(f"Value changed: {current_timestamp}")
                
                last_timestamp = current_timestamp
                
                user_code = get_user_code()
                if user_code:
                    execute_code(user_code)
                else:
                    print("No code found in the environment variable.")
            
            time.sleep(int(REDIS_MONITORING_PERIOD_SECONDS))
        
        except redis.ConnectionError as e:
            print(f"Redis connection error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
