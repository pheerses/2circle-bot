package queue

import (
	"context"
	"github.com/redis/go-redis/v9"
	"os"
)

var rdb = redis.NewClient(&redis.Options{
	Addr: os.Getenv("REDIS_ADDR"),
})

type VideoTask struct {
	InputPath  string `json:"input_path"`
	OutputPath string `json:"output_path"`
	UserID     int64  `json:"user_id"`
	ChatID     int64  `json:"chat_id"`
	MessageID  int    `json:"message_id"`
}

func PopTask(ctx context.Context) (string, error) {
	return rdb.LPop(ctx, "video_tasks").Result()
}

func PushReadyTask(ctx context.Context, task string) error {
	return rdb.RPush(ctx, "video_ready", task).Err()
}