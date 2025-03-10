import json
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(input: dict, context: object) -> dict:
    cpu_history = context.env.get("cpu_history", {})

    for key in input.keys():
        if "cpu_percent-" in key:
            if key not in cpu_history:
                cpu_history[key] = deque(maxlen=12)
            cpu_history[key].append(input[key])

    avg_cpu = {
        f"avg-util-{k}-60sec": sum(v) / len(v)
        for k, v in cpu_history.items()
    }

    percent_network_egress = (
        input["net_io_counters_eth0-bytes_sent"] /
         (input["net_io_counters_eth0-bytes_sent"] +
          input["net_io_counters_eth0-bytes_recv"]) * 100
    )

    percent_memory_cache = (
        ((input["virtual_memory-cached"] +
          input["virtual_memory-buffers"]) /
         input["virtual_memory-total"]) * 100
    )

    result = {
        "percent-network-egress": percent_network_egress,
        "percent-memory-cache": percent_memory_cache,
        **avg_cpu
    }

    context.env["cpu_history"] = cpu_history

    logger.info(f"Resultado: {result}")

    return result
