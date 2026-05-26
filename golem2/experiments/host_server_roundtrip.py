from __future__ import annotations

import json
import time

from ..host.model_host import LMStudioClient, ModelHostClient
from ..host.server import serve


def main() -> None:
    server = serve(port=0)
    base_url = f"http://127.0.0.1:{server.server_port}"
    client = ModelHostClient(base_url)
    llm = LMStudioClient(base_url)
    try:
        sleep = client.start_sleep(
            {
                "ledger_path": "events.jsonl",
                "models": ["heatmap_reader", "urgency_policy"],
                "sampling": {"failures": True},
            }
        )
        time.sleep(0.25)
        result = {
            "health": client.health(),
            "models": client.list_models(),
            "infer": client.infer("heatmap_reader", {"input": {"projection": "distance"}}),
            "train_step": client.train_step("heatmap_reader", {"transition": {"loss": 0.1}}),
            "sleep_start": sleep,
            "sleep_status": client.sleep_status(sleep["job_id"]),
            "lm_models": llm.list_models(),
            "chat": llm.chat_completions({"messages": [{"role": "user", "content": "status"}]}),
        }
        print(json.dumps(result, indent=2))
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
