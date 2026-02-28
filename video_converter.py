import ffmpeg
import uuid
import asyncio

async def convert_to_video_note_async(input_path: str) -> str:
    """Async wrapper to not block the event loop."""
    return await asyncio.to_thread(convert_to_video_note, input_path)

def convert_to_video_note(input_path: str) -> str:
    """Converts a video to a 384x384 square mp4 suitable for Telegram Video Notes."""
    output_path = f"temp_{uuid.uuid4().hex}.mp4"
    try:
        # Check if the video has an audio stream
        try:
            probe = ffmpeg.probe(input_path)
            has_audio = any(stream.get('codec_type') == 'audio' for stream in probe.get('streams', []))
        except Exception:
            has_audio = False

        in_file = ffmpeg.input(input_path)
        video_stream = in_file.video.filter('crop', 'min(iw,ih)', 'min(iw,ih)').filter('scale', 384, 384)
        
        if has_audio:
            audio_stream = in_file.audio
            out = ffmpeg.output(video_stream, audio_stream, output_path, vcodec='libx264', acodec='aac', format='mp4', preset='fast', crf=24)
        else:
            out = ffmpeg.output(video_stream, output_path, vcodec='libx264', format='mp4', preset='fast', crf=24)
            
        out.overwrite_output().run(capture_stdout=True, capture_stderr=True)
        
        return output_path
    except ffmpeg.Error as e:
        if e.stdout:
            print('stdout:', e.stdout.decode('utf8', errors='replace'))
        if e.stderr:
            print('stderr:', e.stderr.decode('utf8', errors='replace'))
        raise e
