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
        (
            ffmpeg
            .input(input_path)
            .filter('crop', 'min(iw,ih)', 'min(iw,ih)')
            .filter('scale', 384, 384)
            .output(output_path, vcodec='libx264', acodec='aac', format='mp4', preset='fast', crf=24)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e
