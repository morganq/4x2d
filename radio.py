import miniaudio


def run_radio(q):
    def title_printer(client: miniaudio.IceCastClient, new_title: str) -> None:
        print("Stream title: ", new_title)

    with miniaudio.IceCastClient(
            "http://23.237.150.178:9002",
            update_stream_title=title_printer
        ) as source:

        #print("Connected to internet stream, audio format:", source.audio_format.name)
        #print("Station name: ", source.station_name)
        #print("Station genre: ", source.station_genre)
        #print("Press <enter> to quit playing.\n")
        stream = miniaudio.stream_any(source, source.audio_format)
        with miniaudio.PlaybackDevice() as device:
            device.start(stream)
            something = q.get()
            print(something)
            
