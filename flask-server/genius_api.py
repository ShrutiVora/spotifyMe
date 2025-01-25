
import lyricsgenius
from google.cloud import translate_v2 as translate
import pandas as pd 
import os.path
import time
import re
import time
import requests
CLIENT_ID="zcu4LXMVp2jdQSbEFQ5V1E1-tNJTQVU3g1emrR2NfZXgZ2-HKe8iFwG5jsBRi1KE"
CLIENT_SECRET="vl3rDnZShugb_kIIv_R-FVISIKaw0-e-ipTZifhYZQSwh4mYgp79cqOfHVF8Ymj2Is5nVKBC96AzeW1obmzXUQ"
CLIENT_ACCESS_TOKEN="4By_Li1nhAhsw6qSi4FqXk-GsbGv87ykVFp_8MAmFswGWaGqOdpRgRP5RgL3i4Vv"
df=pd.read_csv("spotify_tracks.csv")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your-service-account-file.json"
translate_client = translate.Client()
genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN, remove_section_headers=True, skip_non_songs=True, timeout=10)

def clean_title(title):
    # Remove anything in parentheses
    return re.sub(r'\(.*?\)', '', title).strip()

def fetch_lyrics(track_name, track_artists, retries=3):
    for i in range(retries):
        try:
            song = genius.search_song(title=track_name, artist=track_artists)
            if song:
                lyrics = song.lyrics
                # Extract lyrics between "Lyrics" and "Embed"
                pattern = re.compile(r'Lyrics(.*?)Embed', re.DOTALL)
                matches = pattern.findall(lyrics)
                if matches:
                    clean_lyrics = matches[0].replace('\n', ' ').strip()
                else:
                    clean_lyrics = lyrics.replace('\n', ' ').strip()
                return clean_lyrics
            else:
                artists_list = [artist.strip() for artist in track_artists.split(',')]
                print(artists_list)
                for a in artists_list:
                    song=genius.search_song(title=track_name,artist=a)
                    if song:
                        lyrics = song.lyrics
                    # Extract lyrics between "Lyrics" and "Embed"
                        pattern = re.compile(r'Lyrics(.*?)Embed', re.DOTALL)
                        matches = pattern.findall(lyrics)
                        if matches:
                            clean_lyrics = matches[0].replace('\n', ' ').strip()
                        else:
                            clean_lyrics = lyrics.replace('\n', ' ').strip()
                        return clean_lyrics
                    '''
                    start_time=time.time()
                    while time.time()-start_time<100:
                        artist=genius.search_artist(a)
                        found = False
                        for song in artist.songs:
                            if song.title.lower().replace(" ", "") == track_name.lower().replace(" ", ""):
                                lyrics_=song.lyrics
                                found = True
                                pattern = re.compile(r'Lyrics(.*?)Embed', re.DOTALL)
                                matches = pattern.findall(lyrics_)
                                if matches:
                                    clean_lyrics = matches[0].replace('\n', ' ').strip()
                                else:
                                    clean_lyrics = lyrics_.replace('\n', ' ').strip()
                                return clean_lyrics
                            '''
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for {track_name} by {track_artists}. Retrying ({i+1}/{retries})...")
            time.sleep(2)  # Wait before retrying
                        
                        

                
            

            
    return "None"

# Initialize list to store lyrics
lyrics_list = []

#for index, row in df.iterrows():
#    track_name = clean_title(row["track_name"])
#    track_artists = row["track_artists"]
#    l = fetch_lyrics(track_name, track_artists)
#    lyrics_list.append(l)

# Add lyrics to DataFrame
   

#df['track_lyrics'] = lyrics_list

def translate_text(text, target='en'):
    try:
        result=translate_client.translate(text,target_language=target)
        return result['translatedText']
    except Exception as e:
        print(f"Error translating text: {e}")
        return None

track_name=df['track_name'][3]
track_artists=df['track_artists'][3]
l=fetch_lyrics(track_name,track_artists)
print(l)
if l:
    translated_lyrics=translate_text(l,"en")
    print("Translated Lyrics: ", translated_lyrics)
else:
    print("No lyrics found")




#df.to_csv("spotify_tracks.csv", index=False)



