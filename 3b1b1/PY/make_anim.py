import moviepy.video.io.ImageSequenceClip

image_files = []
fps = 10
for a in range(360):
    image_files.append(f"Images/{a}.png")
clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
clip.write_videofile(f'color_shift.mp4')
