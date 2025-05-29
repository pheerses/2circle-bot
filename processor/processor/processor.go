package processor

import (
	"fmt"
	"os/exec"
)

func ProcessVideo(input, output string) error {
	cmd := exec.Command(
		"ffmpeg",
		"-i", input,
		"-vf", "crop='min(iw,ih)':'min(iw,ih)',scale=640:640",
		"-c:v", "libx264",
		"-preset", "fast",
		"-crf", "23",
		"-y", output,
	)

	fmt.Println("Running:", cmd.String())
	return cmd.Run()
}
