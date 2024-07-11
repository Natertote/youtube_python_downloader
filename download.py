import streamlit as st
from pytube import YouTube, Playlist
import os
import subprocess
from pathlib import Path

# Fonction de téléchargement de la vidéo avec mise à jour de la barre de progression
def telechargement(lien, path_to_download_folder, quality, format_type, include_audio, progress_bar, step, total_steps):
    try:
        url = YouTube(lien)
        video_title = url.title
        st.write(f"Téléchargement de la vidéo : {video_title}")

        # Télécharger la vidéo ou l'audio
        if format_type == "MP3":
            audio_stream = url.streams.filter(only_audio=True).first()
            audio_file = audio_stream.download(output_path=path_to_download_folder)
            output_file = os.path.splitext(audio_file)[0] + ".mp3"

            progress_bar.progress(step / total_steps + 0.25 / total_steps)

            cmd = [
                'ffmpeg',
                '-i', audio_file,
                '-metadata', f'title={video_title}',
                output_file
            ]

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            os.remove(audio_file)
            progress_bar.progress(step / total_steps + 1.0 / total_steps)

        else:
            if quality == "1080p":
                video_stream = url.streams.filter(res="1080p", mime_type="video/mp4").first()
            elif quality == "720p":
                video_stream = url.streams.filter(res="720p", mime_type="video/mp4").first()
            else:
                video_stream = url.streams.filter(progressive=True, file_extension='mp4').first()

            video_file = video_stream.download(output_path=path_to_download_folder)
            progress_bar.progress(step / total_steps + 0.25 / total_steps)

            if include_audio:
                audio_stream = url.streams.filter(only_audio=True).first()
                audio_file = audio_stream.download(output_path=path_to_download_folder, filename='audio.webm')
                progress_bar.progress(step / total_steps + 0.5 / total_steps)

                output_file = os.path.splitext(video_file)[0] + "_.mp4"
                cmd = [
                    'ffmpeg',
                    '-i', video_file,
                    '-i', audio_file,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-strict', 'experimental',
                    '-metadata', f'title={video_title}',
                    output_file
                ]

                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                os.remove(video_file)
                os.remove(audio_file)
                progress_bar.progress(step / total_steps + 0.75 / total_steps)
            else:
                output_file = video_file

            progress_bar.progress(step / total_steps + 1.0 / total_steps)

        st.success(f"Téléchargement terminé! {video_title}")
        return output_file

    except Exception as e:
        st.error(f"Erreur durant le téléchargement: {str(e)}")
        return None

# Interface utilisateur avec Streamlit
st.title("Téléchargeur YouTube")

lien = st.text_input("Lien (vidéo ou playlist):")
path_to_download_folder = st.text_input("Chemin de téléchargement:", value=str(Path.home() / "Downloads"))

format_type = st.selectbox("Format:", ["MP4", "MP3"])
if format_type == "MP4":
    quality = st.selectbox("Qualité:", ["1080p", "720p", "480p"])
    include_audio = st.checkbox("Inclure l'audio", value=True)
else:
    quality = None
    include_audio = None

if st.button("Télécharger"):
    if lien:
        if "playlist" in lien:
            playlist = Playlist(lien)
            total_videos = len(playlist.video_urls)
            progress_bar = st.progress(0)
            for index, url in enumerate(playlist.video_urls):
                telechargement(url, path_to_download_folder, quality, format_type, include_audio, progress_bar, index, total_videos)
                progress_bar.progress((index + 1) / total_videos)
        else:
            progress_bar = st.progress(0)
            telechargement(lien, path_to_download_folder, quality, format_type, include_audio, progress_bar, 0, 1)
    else:
        st.warning("Veuillez entrer un lien.")
