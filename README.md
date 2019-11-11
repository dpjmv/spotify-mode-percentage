# Spotify mode percentage

Tells you the amount of major and minor tracks in your playlists.

## Usage

First, provide the infos required in `.env.sample` and export them so that the program can find them as environment variables.

Then, you must specify the names of the playlists you want to analyse in the variable `playlist_names`, at the top of the `main()` function.

```
python app.y
```

## Example output

```
Reparition of modes in playlists ['Rock']:
- Major: 60%
- Minor: 40%
```