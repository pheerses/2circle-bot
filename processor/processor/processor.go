package processor

import (
	"fmt"
	"os/exec"
	"os"
)

func ProcessVideo(input, output string) error {
	crf := os.Getenv("FFMPEG_CRF")
	if crf == "" {
		crf = "23"
	}
	cmd := exec.Command(
		"ffmpeg",
		"-i", input,
		"-vf", "crop='min(iw,ih)':'min(iw,ih)',scale=640:640",
		"-c:v", "libx264",
		"-preset", "fast",
		"-crf", crf,
		"-y", output,
	)


	fmt.Println("Running:", cmd.String())
	return cmd.Run()
}
