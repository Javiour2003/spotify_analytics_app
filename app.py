import streamlit as st
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import radarplot
import songrecommendations

my_secret = st.secrets['my_secrets']

auth_manager = SpotifyClientCredentials(client_id=my_secret['SPOTIPY_CLIENT_ID'], client_secret=my_secret['SPOTIPY_CLIENT_SECRET'])
sp = spotipy.Spotify(auth_manager=auth_manager)

st.title("Track Analytics by :green[Spotify]")
st.header("Analyze any :green[track/song] at your fingertips.")

search_choices = ['Song/Track', 'Album']
search_selected = st.sidebar.selectbox("Your search choice please: ", search_choices)

search_keyword = st.text_input(search_selected + "(Keyword Search)")
button_clicked = st.button("Search")

search_results = []
tracks = []
albums = [] 
if search_keyword is not None and len(str(search_keyword))>0:
    if search_selected == 'Song/Track':
        st.write("Start song/track search...")
        tracks = sp.search(q='tracks:'+search_keyword,type='track',limit = 20)
        tracks_list = tracks['tracks']['items']
        if len(tracks_list) > 0:
            for track in tracks_list:
                # st.write(track['name'] + " - By - "+track['artists'][0]['name'])
                search_results.append({'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'popularity': track['popularity']})
    
  
    elif search_selected == 'Album':
        st.write("Start album search...")
        albums = sp.search(q='albums:'+search_keyword,type='album',limit = 20)
        albums_list = albums['albums']['items']
        if len(albums_list) > 0:
            for album in albums_list:
                search_results.append(album['name'] + " - By - " + album['artists'][0]['name'])

selected_album = None
selected_artist = None
selected_track = None
if search_selected == 'Song/Track':
    sorted_results = sorted(search_results, key=lambda x: x['popularity'], reverse=True)
    selected_track = st.selectbox("Select your song/track: ", [f"{track['name']} - By - {track['artist']}" for track in sorted_results])

elif search_selected == 'Album':
    selected_album = st.selectbox("Select your album: ", search_results)

if selected_track is not None and len(tracks)>0:
    track_id = None
    if len(tracks_list) > 0:
        for track in tracks_list:
            str_temp = track['name'] + " - By - " + track['artists'][0]['name']
            if str_temp == selected_track:
                track_id = track['id']
                track_album = track['album']['name']
                img_album = track['album']['images'][1]['url']
                track_preview_url = track['preview_url']

    selected_track_choice = None
    if track_id is not None:
        st.image(img_album,width=250)
        track_choices = ['Song Features', 'Similar Songs Recommendation']
        selected_track_choice = st.sidebar.selectbox('Please select track choice: ', track_choices)
        if selected_track_choice == 'Song Features':
            track_features = sp.audio_features(track_id)
            if track_preview_url is not None:
                st.write(":green[Preview:]")
                st.audio(track_preview_url, format="audio/mp3")
            else:
                st.write(":red[Preview not available]")
            df = pd.DataFrame(track_features)
            df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence',]]
            st.dataframe(df_features)
            theta = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
            radarplot.feature_plot(df_features,theta)
        elif selected_track_choice == 'Similar Songs Recommendation':
            token = songrecommendations.get_token(my_secret['SPOTIPY_CLIENT_ID'],my_secret['SPOTIPY_CLIENT_SECRET'])
            similar_songs_json = songrecommendations.get_track_recommendations(track_id, token)
            recommendation_list = similar_songs_json['tracks']
            recommendation_list_df = pd.DataFrame(recommendation_list)
            recommendation_df = recommendation_list_df[['name','explicit', 'duration_ms', 'popularity']]
            st.dataframe(recommendation_df) 
    else:
        st.write("Please select a track from the list.")

elif selected_album is not None and len(albums) > 0:
    #albums_list = albums['albums']['items']
    album_id = None
    album_uri = None    
    album_name = None
    if len(albums_list) > 0:
        for album in albums_list:
            str_temp = album['name'] + " - By - " + album['artists'][0]['name']
            if selected_album == str_temp:
                album_id = album['id']
                album_uri = album['uri']
                album_name = album['name']
                img_album = album['images'][1]['url']     

    def feature_requested():
        track_features  = sp.audio_features(df_tracks_min['id'][idx]) 
        df = pd.DataFrame(track_features, index=[0])
        df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
        theta = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
        st.dataframe(df_features)
        radarplot.feature_plot(df_features,theta)             

    if album_id is not None:
        st.image(img_album,width=250)
        st.write("Collecting all the tracks for the album : " + f":green[**{album_name}**]")
        album_tracks = sp.album_tracks(album_id)
        df_album_tracks = pd.DataFrame(album_tracks['items'])
        df_tracks_min = df_album_tracks.loc[:,
                        ['name', 'duration_ms', 'explicit','preview_url','id']]


        for idx in df_tracks_min.index:
            minute = int(df_tracks_min['duration_ms'][idx]/60000)
            sec = int(((df_tracks_min['duration_ms'][idx]/60000) - minute)*60)

            with st.container():
                col1, col2, col3, col4 = st.columns((4,4,1,1))
                col1.write(f":green[**{df_tracks_min['name'][idx]}**]")
                col2.write("Duration: "+ f":green[{minute}:{sec} min]")
                col3.write("Explicit:")
                col4.write(f":green[{df_tracks_min['explicit'][idx]}]")
                if df_tracks_min['preview_url'][idx] is not None: 
                    
                    st.write("Preview:")     
                    st.audio(df_tracks_min['preview_url'][idx], format="audio/mp3")
                else:
                    with col1:
                        st.write(":red[Preview not available]")
            with st.expander(":green[See Feature Plot]"):
                track_features  = sp.audio_features(df_tracks_min['id'][idx]) 
                df = pd.DataFrame(track_features, index=[0])
                df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
                theta = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
                st.dataframe(df_features)
                radarplot.feature_plot(df_features,theta)

    


                 
        
            

                    
    

