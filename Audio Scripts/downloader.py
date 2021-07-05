'''
Author: Adam W

Audio downloader for pystream project
Sole purpose is to download audio streams of videos and then convert them to mp3 files via renaming.
'''
from pytube import YouTube, Playlist
from pytube.exceptions import *
import os


def read_urls(filepath: str):
    '''
    Read urls from a text file
    --------------
    Returns: list of urls
    '''
    print("Reading links...")


    urls = open(filepath, 'r')
    queue = urls.readlines()
    urls.close()

    print('Parsing links...')

    # parse for playlists and videos
    video_urls = []
    playlist_urls = []
    for url in queue:
        # Check for videos
        if '/watch?' in url:
            video_urls.append(url)
        elif '/playlist?' in url:
            playlist_urls.append(url)
        else:
            pass
    

    # Get all video links from the playlists in the playlist_urls array using the playlist class
    playlists = []  # List of playlist objects
    for p in playlist_urls:
        playlists.append(Playlist(p))
    # Get links and add them to video urls
    for p in playlists:
        urls_list = p.video_urls # List of urls from the playlist in the loop
        video_urls += urls_list # Add all contents of that list to the existing video_urls list
        

    # Store all individual video links in the queue
    queue = video_urls
    
    return queue


def convert_queue(queue: list):
    '''
    Creates a list of youtube objects
    --------------------
    Returns list of youtube objects
    '''
    yt_list = []; skipped = [];
    for i in range(len(queue)):
        
        # Check if link is valid
        try:
            yt_list.append(YouTube(queue[i]))
        except RegexMatchError:
            print('Cannot use:', queue[i])
            skipped.append(queue[i])
        
    # Check availibility of videos
    print('Checking for video availibility...')
    
    i = 0
    for yt in yt_list:

        try:
            yt.check_availability()
        except VideoPrivate:

            # Error for video link
            if '/watch?' in queue[i]:
                print(f'Video: https://www.youtube.com/watch?v={yt.video_id} is a PRIVATE VIDEO')
                print('https://www.youtube.com/watch?v=' + yt_list[i].video_id, 'is being removed')
                skipped.append('Video: https://www.youtube.com/watch?v=' + yt_list[i].video_id)
                del yt_list[i]

            # Error for playlist link
            elif '/playlist?' in queue[i]:
                print(f'Playlist: https://www.youtube.com/playlist?v={yt.video_id} is a PRIVATE VIDEO')
                print('https://www.youtube.com/playlist?v=' + yt_list[i].video_id, 'is being removed')
                skipped.append('Video: https://www.youtube.com/playlist?v=' + yt_list[i].video_id)
                del yt_list[i]
        except VideoUnavailable:

            # Error for video link
            if '/watch?' in queue[i]:
                print(f'Video: https://www.youtube.com/watch?v={yt.video_id} is UNAVAILIBLE')
                print('https://www.youtube.com/watch?v=' + yt_list[i].video_id, 'is being removed')
                skipped.append('Video: https://www.youtube.com/watch?v=' + yt_list[i].video_id)
                del yt_list[i]

            # Error for playlist link
            elif '/playlist?' in queue[i]:
                print(f'Playlist: https://www.youtube.com/playlist?v={yt.video_id} is a PRIVATE VIDEO')
                print('https://www.youtube.com/playlist?v=' + yt_list[i].video_id, 'is being removed')
                skipped.append('Video: https://www.youtube.com/playlist?v=' + yt_list[i].video_id)
                del yt_list[i]
        i += 1

    # Write skipped videos to a file
    if len(skipped) > 0:
        print('Logging skipped')
        skipped_log = open('skipped.txt', 'w')

        for i in range(len(skipped)):    
            skipped_log.write(skipped[i] + "\n")
        
        skipped_log.close()
    else: 
        pass

    return yt_list

def ready_audio_queue(yt_list: list):
    '''
    Prepares list of audio streams
    -----------------
    Returns a list of stream objects to download
    '''
    print("Please wait while download streams are initialized...")

    streams = []
    for yt in yt_list:
        streams.append(yt.streams.get_audio_only())
        
        
    return streams


def download_streams(streams):
    '''
    Downloads all the videos to a folder named "Audios"
    -----------
    Returns nothing: Void
    '''

    print('Preparing to download streams...')
    print('Audios folder will be created if it does not already exist')

    # File path
    cwd = os.getcwd()
    path = os.path.join(cwd, 'Audio Scripts','Audios')

    i = 1
    for stream in streams:
        print(f'Download queue: Commencing download number {i}')
        stream.download(path)
        print(f'Download({i}) has finished!')
        i += 1

def generate_mp4_paths():
    '''
    Creates list of mp4 file paths in 'Audios' directory
    ----------------------
    Retuns: list of mp4 file paths
    '''

    # Grab names of all files
    mp4_files = []
    mp4_files = os.listdir('Audios')
    # Create new list of mp4 file paths with mp4 filenames
    mp4_filepaths = []
    for mp4 in mp4_files:
        mp4_filepaths.append(os.path.join('Audios', mp4))

    return mp4_filepaths
        

def mkmp3(mp4_filepaths):
    '''
    Changes the file extension of all mp4 files in the Audios folder
    -----------------------
    Returns nothing: void
    '''
    print('Please wait...')
    print("Converting all files to mp3 format")

    for mp4 in mp4_filepaths:
        # Create new mp3 path string for each and every mp4 path string
        mp3_filepath = mp4.replace('.mp4', '.mp3')
        # Use mp3 string to rename the old mp4 file; via its old file path
        try:
            os.rename(mp4, mp3_filepath)
        except FileExistsError:
            print(f"File: '{mp3_filepath}' already exists")
            print("Aborting conversion")
            pass
    print('All files converted!')

# Lists (used as parameters for next function)
queue = []
yt_list = []
streams = []

# Order of  use (how to use the downloader program)
cwd = os.getcwd()
filepath = os.path.join(cwd, 'Audio Scripts', 'urls.txt')   # Relative to root directory
q = read_urls(filepath) # Save the queue list to a variable
yt_list = convert_queue(q)  # Pass the queue list variable to the convert_queue function
streams = ready_audio_queue(yt_list)    # Finially save the list of streams to another variable 
download_streams(streams)   # Pass the stream list to the download function

# Rename files
mp4_paths = generate_mp4_paths()
mkmp3(mp4_paths)