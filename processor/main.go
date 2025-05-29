package main

import (
	"context"
	"encoding/json"
	"log"
	"time"
    "processor/queue"
    "processor/processor"
	"github.com/redis/go-redis/v9"
)

func main() {
	ctx := context.Background()

	for {
		taskJSON, err := queue.PopTask(ctx)

		if err == redis.Nil {
			time.Sleep(1 * time.Second)
			continue
		} else if err != nil {
			log.Println("Ошибка получения задачи:", err)
			time.Sleep(1 * time.Second)
			continue
		}

		if taskJSON == "" {
			time.Sleep(1 * time.Second)
			continue
		}

		var task queue.VideoTask
		if err := json.Unmarshal([]byte(taskJSON), &task); err != nil {
			log.Println("Ошибка парсинга JSON:", err)
			continue
		}

		log.Printf("Обработка: %s → %s\n", task.InputPath, task.OutputPath)
		err = processor.ProcessVideo(task.InputPath, task.OutputPath)
		if err != nil {
			log.Println("Ошибка обработки видео:", err)
			continue
		}

		taskReadyJSON, _ := json.Marshal(task)
		err = queue.PushReadyTask(ctx, string(taskReadyJSON))
		if err != nil {
			log.Println("Ошибка возврата задачи:", err)
		}


		log.Println("Готово:", task.OutputPath)
	}
}
