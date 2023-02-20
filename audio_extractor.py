from pytube import YouTube as yt
from pytube.cli import on_progress
from pydub import AudioSegment
import os
import time


# Receives the video url
def youtube_downloader(url):
	# Folder to save the videos
	video_save_path = os.path.join("videos")
	if not os.path.exists(video_save_path):
		os.makedirs(video_save_path)
	
	# Loads the video
	yt_video = yt(url, on_progress_callback=on_progress) 
	streams = yt_video.streams
	# Attempt to solve a problem with thumbs which doesnt end with "jpg" or other extension
	thumb = yt_video.thumbnail_url.split("?")[0]
	audio = streams.get_audio_only()	# Gets audio only stream, but still mp4
	title = audio.title
	print(f"\nPreparing to download {title}")
	title = title.replace("|", "")

	print(f"File size: {audio.filesize_mb}mb")
	file = audio.download(video_save_path)

	return [file, title, thumb]


# Receives an AudioSegment
def audio_converter(audio, title, thumb):
	# Folder to save the audios
	audio_save_path = os.path.join("audios")
	if not os.path.exists(audio_save_path):
		os.makedirs(audio_save_path)

	# Extracts the audio from the mp4
	print("Converting to audio file...")
	audio_save_path = os.path.join(audio_save_path, title)
	audio.export(f"{audio_save_path}.mp3", format="mp3", cover=thumb)

	return audio_save_path


# Receives an AudioSegment, the time to start and end
def audio_splitter(audio, start, end):
	start = start.split(":")
	end = end.split(":")
	# Converts if times are above 60 seconds,
	# E.g.: user types only 37 as start
	if len(start) > 1:
		start[0] = (int(start[0]) * 60 + int(start[1]))
	if len(end) > 1:
		end[0] = (int(end[0]) * 60 + int(end[1]))
	audio_isolated = audio[int(start[0])*1000:int(end[0])*1000]
	audio_final = audio_isolated.fade_in(5 * 1000).fade_out(5 * 1000)
	
	return audio_final


def run():
	video_url = input("Paste the video url here: ")
	video_ouput = youtube_downloader(video_url)
	print("\nDownloaded")
	audio = AudioSegment.from_file(video_ouput[0])

	while True:
		# Try catch everything cause Im lazy....
		try:
			splitting = input("\nDo you want to convert only a part of the audio? (y/N) ")
			if splitting == "" or splitting.lower() == "n":
				audio_converter(audio, video_ouput[1], video_ouput[2])
				break
			elif splitting.lower() == "y":
				start = input("When should the audio start? E.g.: (31 or 1:47) ")
				end = input("And when should it end? E.g.: (31 or 1:47) ")
				audio_splitted = audio_splitter(audio, start, end)
				audio_converter(audio_splitted, video_ouput[1], video_ouput[2])
				break
		except Exception as e:
			print(e)
			print("Something went wrong while converting, please type again.\n"
				"If you want to end the process just type \"n\" to convert the whole audio.")

	print("\nCompleted")


if __name__ == "__main__":
	run()
