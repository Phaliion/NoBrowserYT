import tkinter.messagebox
from typing import Any
import time as timelib
import os, tkinter
from pygame import mixer, time, error
from pydub import AudioSegment
from threading import Thread
from pytube import *

# used for smooth swap between files
hotswap : bool = False
current_song_length : int = 0

def init() -> None:
    if mixer.get_init() != None: 
        raise Exception("Mixer already initialized")
    
    mixer.pre_init(44100, 32, 2, 4096)
    mixer.init()

def null_check(value : Any) -> None:
    if value == None: 
        raise Exception("Null filepath")

def load_file(filepath : str | None = None) -> None:
    null_check(filepath)
    global hotswap, current_song_length
    hotswap = not hotswap
    # convert to format pygame likes
    audio = AudioSegment.from_file(filepath)
    audio.export(fr"temp\tempaudio{int(hotswap)}.wav", format="wav")
    current_song_length = int(mixer.Sound(fr"temp\tempaudio{int(hotswap)}.wav").get_length())
    mixer.music.load(fr"temp\tempaudio{int(hotswap)}.wav")

def volume(volume : float | None = None) -> None:
    """
    value between 0-1
    """
    null_check(volume)
    mixer.music.set_volume(volume)

def position(pos : float | None = None) -> None:
    null_check(pos)
    if not mixer.music.get_busy():
        raise Exception("Cannot set position, mixer is not playing")
    try:
        mixer.music.set_pos(pos)
    except error:
        print("Error setting pos")
        mixer.music.stop()

def play(filename : str | None = None) -> None:
    global hotswap
    if filename != None:
        load_file(filename)
    if mixer.music.get_busy():
        stop()
    mixer.music.play()
def stop() -> None:
    mixer.music.stop()

################################################ PYTUBE STUFF ###################################################
def search(query : str | None = None, index : int | None = None) -> YouTube | list[YouTube]:
    null_check(query)
    search = Search(query)

    if index == None:
        return search.results
    
    if index >= len(search.results):
        index = -1
    return search.results[index]

def no_illegal_chars(string : str):
    for x in ['#','$','%','^','&','{','}','\\','<','>','*','?','/','!',"'",'"',':','@','+','`','|','=']:
        string = string.replace(x, "")
    return string

def video_to_dir(video : YouTube) -> str:
    dir : str = video.title
    # remove illegal char
    dir = no_illegal_chars(dir)
    dir = fr"{dir}...{video.video_id}.wav"
    return dir


def download(video : YouTube | None = None) -> str:
    null_check(video)
    start = timelib.time()
    print(video.title)
    stream = video.streams.get_audio_only()
    print(f"Downloading {video.title}")
    new_title : str = video.title
    # remove illegal char
    new_title = no_illegal_chars(new_title)
    try:
        stream.download(filename=fr"temp\{new_title}...{video.video_id}.wav") # output_path=temp_file.name
    except Exception as e:
        tkinter.messagebox.showinfo("Error 400", "Could not download song")
        raise Exception(e)
    print(f"Download Complete:\t {timelib.time() - start}s")
    return fr"temp\{new_title}...{video.video_id}.wav"