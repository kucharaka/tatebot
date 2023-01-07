import discord
import asyncio
import youtube_dl
import config

# Discord bot Initialization
intents = discord.Intents().all()
client = discord.Client(intents=intents)
key = 'UR TOKEN HERE'

voice_clients = {}

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'options': "-vn"}

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")


@client.event
async def on_message(msg):
    # Initialize the music queue for each server
    if not hasattr(client, 'music_queues'):
        client.music_queues = {}

    # Check if the server has a music queue, and if not, create one
    if msg.guild.id not in client.music_queues:
        client.music_queues[msg.guild.id] = asyncio.Queue()

    # Get the music queue for the server
    music_queue = client.music_queues[msg.guild.id]

    if msg.content.startswith("$TOPG"):
        try:
            voice_client = await msg.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except:
            print("error")
        try:
            url = msg.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

            # Add the song to the music queue
            await music_queue.put(player)

            # If the voice client is not playing anything, start playing the song
            if not voice_clients[msg.guild.id].is_playing():
                await play_next_song(voice_clients[msg.guild.id], music_queue)
        except Exception as err:
            print(err)

    if msg.content.startswith("$STOPG"):
        try:
            voice_clients[msg.guild.id].pause()
        except Exception as err:
            print(err)


async def play_next_song(voice_client, music_queue):
    # Get the next song in the queue
    player = await music_queue.get()

    # Start playing the song
    voice_client.play(player)

    # Wait for the song to finish
    while voice_client.is_playing():
        await asyncio.sleep(1)

    # Once the song is finished, play the next song in the queue (if there is one)
    if not music_queue.empty():
        await play_next_song(voice_client, music_queue)
    # If there are no more songs in the queue, disconnect from the voice channel
    else:
        await voice_client.disconnect()


client.run(key)
