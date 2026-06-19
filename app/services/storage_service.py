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
    try:
        supabase_client.storage.from_(
            bucket_name
        ).upload(
            path=unique_name,
            file=file_bytes,
            file_options={
                "content-type": mime_type
            }
        )
    except AttributeError as e:
        # Bypass the storage3 SDK bug where it accesses '.text' on a parsed JSON dict
        cause = e.__context__  # KeyError
        if cause and hasattr(cause, '__context__'):
            http_err = cause.__context__  # HTTPStatusError
            if http_err and hasattr(http_err, 'response'):
                status_code = http_err.response.status_code
                response_text = http_err.response.text
                raise Exception(f"Supabase Storage error (HTTP {status_code}): {response_text}") from e
        raise Exception(f"Supabase Storage upload failed due to SDK parsing error: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Supabase Storage upload failed: {str(e)}") from e

    # Generate signed URL (7 days)
    # NOTE: The storage bucket is private for security.
    # Signed URLs generated here will expire after 7 days (604800 seconds).
    # Future improvement: Store the raw storage path in the database instead of the signed URL,
    # and generate fresh signed URLs on-demand when requested by the user.
    try:
        signed_url_response = (
            supabase_client
            .storage
            .from_(bucket_name)
            .create_signed_url(
                unique_name,
                60 * 60 * 24 * 7
            )
        )
    except AttributeError as e:
        cause = e.__context__  # KeyError
        if cause and hasattr(cause, '__context__'):
            http_err = cause.__context__  # HTTPStatusError
            if http_err and hasattr(http_err, 'response'):
                status_code = http_err.response.status_code
                response_text = http_err.response.text
                raise Exception(f"Supabase Storage signed URL generation failed (HTTP {status_code}): {response_text}") from e
        raise Exception(f"Supabase Storage signed URL generation failed due to SDK parsing error: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Supabase Storage signed URL generation failed: {str(e)}") from e

    return signed_url_response["signedURL"]