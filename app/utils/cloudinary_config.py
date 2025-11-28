import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_profile_image(file_bytes: bytes, user_id: int, filename: str) -> dict:
    import logging
    logger = logging.getLogger("cloudinary_upload")
    try:
        log_msg = f"Subiendo imagen a Cloudinary para user_id={user_id}, filename={filename}"
        logger.info(log_msg)
        print(log_msg)
        import uuid
        result = cloudinary.uploader.upload(
            file_bytes,
            folder="steam_group/profiles",
            public_id=f"user_{user_id}_{uuid.uuid4()}",
            unique_filename=True,
            overwrite=False,
            invalidate=True,
            resource_type="image",
            transformation=[
                {
                    "width": 500,
                    "height": 500,
                    "crop": "fill",
                    "gravity": "face",
                    "quality": "auto:best",
                    "fetch_format": "auto"
                }
            ],
            eager=[
                {
                    "width": 200,
                    "height": 200,
                    "crop": "fill",
                    "gravity": "face",
                    "quality": "auto:good",
                    "fetch_format": "auto"
                },
                {
                    "width": 100,
                    "height": 100,
                    "crop": "fill",
                    "gravity": "face",
                    "quality": "auto:good",
                    "fetch_format": "auto"
                }
            ]
        )
        logger.info(f"Respuesta de Cloudinary: {result}")
        print(f"Respuesta de Cloudinary: {result}")
        return {
            "url": result.get("secure_url"),
            "url_thumbnail": result.get("eager")[0].get("secure_url") if result.get("eager") else None,
            "url_small": result.get("eager")[1].get("secure_url") if len(result.get("eager", [])) > 1 else None,
            "public_id": result.get("public_id"),
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "bytes": result.get("bytes")
        }
    except Exception as e:
        logger.error(f"Error al subir imagen a Cloudinary: {str(e)}")
        print(f"Error al subir imagen a Cloudinary: {str(e)}")
        raise Exception(f"Error al subir imagen a Cloudinary: {str(e)}")

def delete_profile_image(public_id: str) -> bool:
    try:
        result = cloudinary.uploader.destroy(public_id, invalidate=True)
        return result.get("result") == "ok"
    except Exception as e:
        raise Exception(f"Error al eliminar imagen de Cloudinary: {str(e)}")
