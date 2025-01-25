import requests
import pandas as pd 
url="http://127.0.0.1:5001/fetch-all-tracks"
response=requests.get(url)
data=response.json()



tracks=data['tracks']

track_details=[]
for track in tracks:
    if ((track is not None)):
        track_id=track['id']
        track_artists=",".join([artist['name'] for artist in track['artists']])
        track_name=track['name']
        track_details.append({
            "track_id":track_id,
            "track_name":track_name,
            "track_artists":track_artists
        })

    
df=pd.DataFrame(track_details,columns=['track_id','track_name',"track_artists"])
df['track_name'].replace('', pd.NA, inplace=True)
df=df.drop_duplicates()
df=df.dropna(subset=["track_name"])
df.to_csv("spotify_tracks.csv", index=False)

#print(df.head())

