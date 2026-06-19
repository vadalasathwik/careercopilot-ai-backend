import os
import uuid
import mimetypes

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_SERVICE_ROLE_KEY is missing"
    )

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing"
    )

# Remove /rest/v1 if someone pasted the API URL
if SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL.replace("/rest/v1", "")

if SUPABASE_URL.endswith("/rest/v1/"):
    SUPABASE_URL = SUPABASE_URL.replace("/rest/v1/", "")

supabase_client: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def upload_file_to_storage(
    file_bytes: bytes,
    file_name: str,
    bucket_name: str = "resumes"
) -> str:
    """
    Upload file to Supabase Storage
    and return a signed URL.
    """

    file_ext = os.path.splitext(file_name)[1].lower()

    unique_name = (
        f"{uuid.uuid4()}{file_ext}"
    )

    mime_type, _ = mimetypes.guess_type(
        file_name
    )

    if not mime_type:
        if file_ext == ".pdf":
            mime_type = "application/pdf"
        elif file_ext == ".docx":
            mime_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            mime_type = "application/octet-stream"

    # Upload file
    supabase_client.storage.from_(
        bucket_name
    ).upload(
        path=unique_name,
        file=file_bytes,
        file_options={
            "content-type": mime_type
        }
    )

    # Generate signed URL (7 days)
    signed_url_response = (
        supabase_client
        .storage
        .from_(bucket_name)
        .create_signed_url(
            unique_name,
            60 * 60 * 24 * 7
        )
    )

    return signed_url_response["signedURL"]