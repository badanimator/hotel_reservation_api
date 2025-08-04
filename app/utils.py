from PIL import Image
from io import BytesIO
from datetime import datetime, time, timezone
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def get_limit_payload(request_limit):
    now = time()
    wait = round(request_limit.reset_at - now, 2)
    next_time = datetime.fromtimestamp(request_limit.reset_at, tz=timezone.utc).isoformat()

    return {
        "retry_after_seconds": wait,
        "next_request_time_utc": next_time,
    }


def is_max_size_exceeded(file: FileStorage, max_size=5 * 1024 * 1024) -> bool:
    file.seek(0, 2)  # Move to end of file
    size = file.tell()
    file.seek(0)  # Reset file pointer
    return size > max_size
    

def is_image(file: FileStorage):
    try:
        Image.open(file).verify()
        file.seek(0)
        return True
    except Exception:
        return False


def compress_image(file:FileStorage, max_size=(800, 800), format="WEBP", quality=60):
    """
    Compresses an image to be small while maintaining quality.
    
    Args:
        file: a FileStorage or BytesIO object
        max_size: tuple of max (width, height)
        format: 'WEBP' or 'JPEG'
        quality: 1-100 (higher = better quality, larger size)

    Returns:
        (binary_data, mime_type, filename)
    """
    
    image = Image.open(file)
    filename = secure_filename(file.filename)

    # Resize while maintaining aspect ratio
    image.thumbnail(max_size)

    # Convert to RGB to avoid mode errors
    image = image.convert("RGB")

    # Compress into memory
    buffer = BytesIO()
    image.save(buffer, format=format, quality=quality, optimize=True)
    buffer.seek(0)

    mime = f"image/{format.lower()}"
    return buffer.getvalue(), mime, filename
