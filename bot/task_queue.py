import redis
import json
import os

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)

async def enqueue_task(task: dict):
    r.rpush("video_tasks", json.dumps(task))

def get_ready_task():
    task_json = r.lpop("video_ready")
    if task_json:
        return json.loads(task_json)
    return None
