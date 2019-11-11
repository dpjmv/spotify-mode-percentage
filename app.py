import spotipy
import sys
import spotipy.util as util
import os


def connectToSpotify(username):
    """
    Default constructor

    :param username: 
        Username of the user to interact with.
    
    :returns:
        A spotipy.Spotify object that can then be used to interact
        with the Spotify Web API
    """
    scopes = 'playlist-read-private playlist-read-collaborative ' + \
        'playlist-modify-public playlist-modify-private'

    token = util.prompt_for_user_token(username, scopes)
    if not token:
        print(f"No token for user {username}")
        sys.exit()
    
    return spotipy.Spotify(auth=token)


def getTrackIds(sp, username, playlist, offset=0):
    """
    Returns the ids of the tracks contained in a playlist

    :param sp:
        A spotipy.Spotify object to be used for the request.

    :param username:
        The username of the user who's playlists you want the retrieve.

    :param playlist:
        Name of the playlist from wich the tracks are retrieved.

    :param offset:
        Do not worry about this parameter, it is used for recursion.
    
    :returns:
        A list containing all the ids of the tracks that are in the playlist.
    """
    limit = 100
    fields = "items(track(id)), total"

    api_response = sp.user_playlist_tracks(username,
        playlist["id"], fields, limit=limit, offset=offset)

    track_ids = [x["track"]["id"] for x in api_response["items"]]

    if api_response["total"] > limit + offset:
        next_page = getTrackIds(sp, username, playlist, offset + limit)
        for item in next_page:
            track_ids.append(item)
    
    return track_ids


def getPlaylists(sp, username, offset=0):
    """
    Retrieves all the playlists a user has

    :param sp:
        A spotipy.Spotify object to be used for the request.

    :param username:
        The username of the user who's playlists you want the retrieve.
    
    :param offset:
        Do not worry about this parameter, it is used for recursion.
    
    :returns:
        A dict containing all of the user's playlists.
    """
    limit = 50

    api_response = sp.user_playlists(username, limit, offset)

    playlists = [x for x in api_response["items"]]

    if api_response["total"] > limit + offset:
        next_playlists = getPlaylists(sp, username, offset + limit)
        for playlist in next_playlists:
            playlists.append(playlist)
    
    return playlists


def getPlaylistsByName(sp, username, playlist_names):
    playlists = []
    for playlist in getPlaylists(sp, username):
        if playlist["name"] in playlist_names:
            playlists.append(playlist)

    return playlists


def getAudioFeatures(sp, tracks):
    track_features = []
    iteration = 0
    while len(track_features) < len(tracks):
        upper_limit = (iteration + 1) * 50
        lower_limit = iteration * 50
        request_data = tracks[lower_limit:upper_limit]
        api_response = sp.audio_features(request_data)
        track_features = track_features + api_response
        iteration += 1

    return track_features


def main():
    # PLaylists to analyse, they have to be among your saved playlists
    playlist_names = ["Ω"]

    # Retrieve username
    username = os.getenv("SPFY_MODE_USERNAME")

    if len(sys.argv) > 1:
        username = sys.argv[1]
    elif username:
        pass
    else:
        print(f"Usage: {sys.argv[0]} username")
        sys.exit()

    # Connect to spotify
    sp = connectToSpotify(username)

    # get playlist ids
    playlists = getPlaylistsByName(sp, username, playlist_names)

    tracks = []
    for playlist in playlists:
        tracks = tracks + getTrackIds(sp, username, playlist)

    track_with_features = getAudioFeatures(sp, tracks)
    count_by_mode = {"minor": 0, "major": 0}
    for track in track_with_features:
        mode = track["mode"]
        if mode == 0:
            count_by_mode["minor"] += 1
        elif mode == 1:
            count_by_mode["major"] += 1

    coefficient = 100 / len(tracks)
    perc_major = count_by_mode["major"] * coefficient
    perc_minor = count_by_mode["minor"] * coefficient

    print(f"Reparition of modes in playlists {playlist_names}:")
    print(f"- Major: {round(perc_major)}%")
    print(f"- Minor: {round(perc_minor)}%")


main()