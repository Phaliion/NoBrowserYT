from io import TextIOWrapper
import tkinter as Tk
from tkinter import font, ttk, messagebox as mb
from tkinter.simpledialog import askstring
import os, shutil
import mixercontrols as mc

BLANK = ' '
FILLED = '⬤'

MAX_VOL : int = 0.002 # 1 = 100%


path : str = os.getcwd()
### CHECK IF playlists/saved/temp dirs exist
if not os.path.isdir(os.path.join(path, "playlists")):
    os.makedirs(os.path.join(path, "playlists"))
    
if not os.path.isdir(os.path.join(path, "temp")):
    os.makedirs(os.path.join(path, "temp"))

if not os.path.isdir(os.path.join(path, "saved")):
    os.makedirs(os.path.join(path, "saved"))


window = Tk.Tk()
mc.init()
window.state('zoomed')
window.title("No Browser YT")
window.config(bg='#1e2124')
#################################### DIFFERENT TAB STUFF ######################################
tabController = ttk.Notebook(window)
tempTab = ttk.Frame(tabController)
permTab = ttk.Frame(tabController)
playlistTab = ttk.Frame(tabController)
tabController.add(tempTab, text ='Queue') 
tabController.add(permTab, text ='Saved')
tabController.add(playlistTab, text="Playlists")
tabController.pack(expand=1, fill="both")

##################################### SAVED STUFF ######################################
def queryitemCutoff(string : str) -> str:
    return string[:70] + ("..." if len(string) > 70 else "")

queueList : Tk.Listbox   
savedList : Tk.Listbox
playList : Tk.Listbox
queueListIDMap : list[str] = []
savedListIDMap : list[str] = []
playListIDMap : list[str] = []
def save_to_queue(*args):
    global queueList, queueListIDMap, savedListIDMap
    index : int = savedList.nearest(args[0].y)
    if savedListIDMap[index] in queueListIDMap:
        print("Already selected")
        return
    old_string : str = savedList.get(index)
    savedList.delete(index)
    savedList.insert(index, old_string.replace(BLANK, FILLED))
    queueList.insert(Tk.END, old_string)
    queueListIDMap.append(savedListIDMap[index])
    #shutil.copyfile(fr"saved\{savedListIDMap[index]}", fr"temp\{savedListIDMap[index]}")

text3 = Tk.Label(permTab, text = "Saved", width=70, height=2, font=font.Font(size = 15), background="#FFFFFF")
text3.place(x=0,y=0)

savedList = Tk.Listbox(permTab, width=70, height=30, font=font.Font(size = 15))
savedList.bind("<Double-1>", save_to_queue)
savedList.place(x=0,y=50)

# populate savedList
i = False
for filename in os.listdir("saved"):
    f = os.path.join("saved", filename)
    if os.path.isfile(f) and filename.endswith(".wav"):
        i = not i
        savedListIDMap.append(f)
        savedList.insert(Tk.END, BLANK+queryitemCutoff(filename.split("...")[0]))

# clear any temp files
for filename in os.listdir("temp"):
    f = os.path.join("temp", filename)
    if os.path.isfile(f) and filename.endswith(".wav"):
        try:
            os.remove(f)
        except:...

#################################### queue stuff ##################################
current_song_label : Tk.Label
current_song_index : int = None
ended_on_own : bool
isPaused = False
isLooping = False
pauseButton : Tk.Button
def queueListSelected(*args):
    global queueList, queueListIDMap, isPaused, isLooping, ended_on_own, current_song_index
    ended_on_own = False
    if current_song_index != None and not isLooping:
        new_string : str = str(queueList.get(current_song_index)).replace(FILLED, BLANK)
        queueList.delete(current_song_index)
        queueList.insert(current_song_index, new_string)
    if args[0] == None and isLooping:...
    elif args[0] == None:
        current_song_index += 1
    else:
        current_song_index = queueList.nearest(args[0].y)
    if not isLooping:
        new_string = str(queueList.get(current_song_index)).replace(BLANK, FILLED)
        queueList.delete(current_song_index)
        queueList.insert(current_song_index, new_string)

    pauseButton.configure(text="Pause")
    current_song_label.configure(text=queueListIDMap[current_song_index].removeprefix('temp\\').removeprefix('saved\\').split("...")[0])
    isPaused = False
    mc.load_file(queueListIDMap[current_song_index])
    mc.play()
    ended_on_own = True
    hang_til_end(True)
def permsave(*args):
    global queueList, savedListIDMap, queueListIDMap, savedList
    index : int = queueList.nearest(args[0].y)
    print(queueListIDMap[index])
    if queueListIDMap[index] in savedListIDMap:
        print("Already saved")
        return
    savedList.insert(Tk.END, queueList.get(index))
    savedListIDMap.append(queueListIDMap[index].replace("temp\\","saved\\"))
    queueListnopref = queueListIDMap[index].removeprefix('temp\\')
    shutil.copyfile(fr"{queueListIDMap[index]}", fr"saved\{queueListnopref}")
    os.remove(queueListIDMap[index])
    queueListIDMap[index] = queueListIDMap[index].replace("temp\\", "saved\\")
def deletetemp(*args):
    global queueList, queueListIDMap, savedListIDMap, savedList
    index : int = queueList.nearest(args[0].y)
    if not queueListIDMap[index].removeprefix('temp\\') in savedListIDMap:
        result = mb.askquestion("Are you sure you want to delete this song? (It is not saved)",
                                queueListIDMap[index].removeprefix('temp\\'))
        if result == 'no': return
    try:
        if not queueListIDMap[index] in savedListIDMap:
            os.remove(queueListIDMap[index])
        else:
            savedIDindex : int = savedListIDMap.index(queueListIDMap[index])
            new_string : str = str(savedList.get(savedIDindex)).replace(FILLED, BLANK)
            savedList.delete(savedIDindex)
            savedList.insert(savedIDindex, new_string)
        queueListIDMap.pop(index)
        queueList.delete(index)
    except:
        print("Unable to delete file")
        

text0 = Tk.Label(tempTab, text = "Queue", width=70, height=2, font=font.Font(size = 15), background="#FFFFFF")
text0.place(x=0,y=0)

queueList = Tk.Listbox(tempTab, width=70, height=30, font=font.Font(size = 15))
queueList.bind("<Double-1>", queueListSelected)
queueList.bind("<Double-3>", permsave)
queueList.bind("<Double-2>", deletetemp)
queueList.place(x=0,y=50)

#################################### search query stuff ##################################
searchList : Tk.Listbox
searchbox : Tk.Text
videoselection : list[mc.YouTube]
def searchListSelected(*args):
    global searchList, videoselection, queueList, queueListIDMap, current_song_index, savedListIDMap
    video : mc.YouTube = videoselection[searchList.curselection()[0]]
    title : str = mc.video_to_dir(video)
    if "temp\\" + title in queueListIDMap or "saved\\" + title in savedListIDMap:
        print("Already downloaded")
        return
    filename = mc.download(video)
    item = str(searchList.get(searchList.curselection()[0]))
    queueList.insert(Tk.END, item)
    queueListIDMap.append(filename)
def commit_query():
    global queueList, window, searchbox, searchList, videoselection, queueListIDMap, savedListIDMap
    query = searchbox.get("1.0", Tk.END).replace("\n", "")
    searchbox.delete("1.0", Tk.END)
    videoselection = mc.search(query)
    videoselection.reverse()
    searchList.delete(0, Tk.END)
    for video in videoselection:
        prefix : str
        title : str = mc.video_to_dir(video)
        if ("temp\\" + title) in queueListIDMap or ("saved\\" + title) in savedListIDMap:
            prefix = FILLED
        else:
            prefix = BLANK
        searchList.insert(0, prefix + queryitemCutoff(video.title))
    videoselection.reverse()
def keyhandler(key):
    if key.char == "\r":
        commit_query()
        return "break"
# entry = Tk.Entry(window)
# entry.place(x=223, y=32)
text1 = Tk.Label(window, text = "Search", width=70, height=2, font=font.Font(size = 15), background="#FFFFFF")
text1.place(x=window.winfo_screenwidth()/2,y=0)

searchList = Tk.Listbox(window, width=70, height=15, font=font.Font(size = 15))
searchList.bind("<Double-1>", searchListSelected)
searchList.place(x=window.winfo_screenwidth()/2,y=50)

searchbox = Tk.Text(window, width=60, height=1, font=font.Font(size = 15))
searchbox.place(x=window.winfo_screenwidth()/2, y=413)
searchbox.bind("<Key>", keyhandler)

searchbutton = Tk.Button(window,text='Search',command=commit_query, width=14, height=1)
searchbutton.place(x=window.winfo_screenwidth()/2 + 665, y=413)
#################################### OTHER STUFF ##################################
volume_value = Tk.DoubleVar(value=32)
time_value = Tk.DoubleVar(value=0)
ended_on_own = True
def __start_wait() -> None:
    global time_value, ended_on_own, queueList, current_song_index
    while mc.mixer.music.get_busy() and ended_on_own:
        mc.time.Clock().tick(10)
        time_value = Tk.DoubleVar(value=int(mc.mixer.music.get_pos() / mc.current_song_length))
        timeslider.set(time_value.get())
    if ended_on_own:
        try:
            queueListSelected(None)
        except:...

def hang_til_end(multithreading : bool = False) -> None:
    if multithreading:
        mc.Thread(None, __start_wait, daemon=True).start()
    else:
        __start_wait()
#################################### CONTROLS ##################################

mc.volume(volume_value.get() * MAX_VOL)
def pause():
    global pauseButton, isPaused, ended_on_own
    if isPaused: # already paused
        pauseButton.configure(text="Pause")
        mc.mixer.music.unpause()
        ended_on_own = True
        hang_til_end(True)
    else:
        pauseButton.configure(text="Resume")
        ended_on_own = False
        mc.mixer.music.pause()

    isPaused = not isPaused
def volumechanged(*args):
    mc.volume(volume_value.get() * MAX_VOL)
def loopbox_click(*args):
    global isLooping
    isLooping = not isLooping
# def timepressed(*args):
#     global thread_disable
#     thread_disable = True
# def timechanged(*args):
#     global thread_disable, time_value
#     thread_disable = False
#     mc.position(time_value.get() * mc.current_song_length)
#     hang_til_end(True)
pauseButton = Tk.Button(window,text='Pause',command=pause, width=10, height=4, font=font.Font(size = 15))
pauseButton.place(x=window.winfo_screenwidth()/2 + 320, y=650)

slider = Tk.Scale(window, variable = volume_value, from_ = 0, to = 100, orient = Tk.HORIZONTAL, label=f"Volume (0%-{MAX_VOL * 100}%)", length=window.winfo_screenwidth()/3) 
slider.place(x=window.winfo_screenwidth()/2+120,y=440)
slider.bind("<ButtonRelease-1>", volumechanged)

timeslider = Tk.Scale(window, variable = time_value, from_ = 0, to = 1_000, orient = Tk.HORIZONTAL, label="Time in Song", length=window.winfo_screenwidth()/3) 
timeslider.place(x=window.winfo_screenwidth()/2+120,y=500)
# timeslider.bind("<ButtonPress-1>", timepressed)
# timeslider.bind("<ButtonRelease-1>", timechanged)

loop_checkbox = Tk.Checkbutton(window, text="Loop")
loop_checkbox.place(x=window.winfo_screenwidth()/2+35,y=450)
loop_checkbox.bind("<ButtonPress-1>", loopbox_click)

current_song_label = Tk.Label(window, width=70, height=2, text="")
current_song_label.place(x=window.winfo_screenwidth()/2+120,y=580)

#################################### PLAYLISTS ##################################
def load_playlist(*args):
    global playList, playListIDMap, queueList, queueListIDMap, savedListIDMap, savedList
    index : int = playList.nearest(args[0].y)
    queueList.delete(0, Tk.END)
    queueListIDMap.clear()
    PLfile = open(playListIDMap[index], 'rb')
    songs : list[str] = PLfile.read().decode('utf8').split(":")
    PLfile.close()
    for song in songs:
        # make sure the song still exists
        if song in savedListIDMap:
            index = savedListIDMap.index(song)
            new_string : int = str(savedList.get(index)).replace(BLANK, FILLED)
            savedList.delete(index)
            savedList.insert(index, new_string)
            queueList.insert(Tk.END, BLANK + queryitemCutoff(song.split("...")[0].removeprefix("saved\\")))
            queueListIDMap.append(song)

def save_playlist():
    global queueList, queueListIDMap, playList, playListIDMap
    prev_name = mc.no_illegal_chars(askstring("Save Playlist", "Save the playlist as: \"\".txt"))
    name = fr"playlists\{prev_name}.txt"
    file : TextIOWrapper
    if name in playListIDMap:
        result = mb.askokcancel("Overwrite", "Are you sure you want to overwrite an existing playlist?")
        # if CANCEL
        if not result:
            return
        file = open(name, 'wb')
    else:
        file = open(name, 'xb')
    
    playListIDMap.append(name)
    playList.insert(Tk.END, prev_name)
    
    i = 0
    for queueID in queueListIDMap:
        if i > 0: file.write(b':')
        i+=1
        file.write(queueID.encode('utf8'))

    file.close()

text5 = Tk.Label(playlistTab, text = "Playlists", width=70, height=2, font=font.Font(size = 15), background="#FFFFFF")
text5.place(x=0,y=0)

playList = Tk.Listbox(playlistTab, width=70, height=30, font=font.Font(size = 15))
playList.bind("<Double-1>", load_playlist)
playList.place(x=0,y=50)

saveButton = Tk.Button(playlistTab,text='Save Playlist',command=save_playlist, width=10, height=1, font=font.Font(size = 7))
saveButton.place(x=window.winfo_screenwidth()/2 + 25, y=735)

# populate playList
for filename in os.listdir("playlists"):
    f = os.path.join("playlists", filename)
    if os.path.isfile(f) and filename.endswith(".txt"):
        playListIDMap.append(f)
        playList.insert(Tk.END, queryitemCutoff(filename.split("...")[0].removesuffix(".txt")))

def on_closing():
    global ended_on_own
    ended_on_own = False
    mc.stop()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()