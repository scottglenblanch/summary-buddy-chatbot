"""
Admin endpoints - Manage RAG pipeline and resources
"""

from flask import Blueprint, request, jsonify, send_file
import os
import tempfile
import logging
from io import BytesIO
from pathlib import Path

from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from app.services.rag_pipeline import get_rag_pipeline
from app.services.storage import StorageService

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# File types accepted for upload
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@admin_bp.route("/upload-document", methods=["POST"])
def upload_document():
    """
    Upload one or more documents (.pdf or .txt) to ingest into the knowledge base.

    Accepts a multipart form field ``files`` containing one or more files. A
    single ``file`` field is also accepted for backward compatibility.

    Each file is converted to text file(s) (PDF -> per-page text files, large
    text files -> smaller text files), persisted to storage (a separate
    storage container locally, S3 in AWS), embedded, and added to the vector
    database.

    Returns:
        JSON describing the aggregate processing result, including a per-file
        ``results`` array.
    """
    try:
        uploads = request.files.getlist("files")
        if not uploads:
            single = request.files.get("file")
            uploads = [single] if single else []

        uploads = [u for u in uploads if u and u.filename]
        if not uploads:
            return jsonify({"status": "failed", "error": "No file provided"}), 400

        pipeline = get_rag_pipeline()
        results = []

        for upload in uploads:
            filename = secure_filename(upload.filename)
            ext = Path(filename).suffix.lower()

            if ext not in ALLOWED_EXTENSIONS:
                results.append({
                    "status": "failed",
                    "filename": filename,
                    "error": f"Unsupported file type '{ext or 'unknown'}'. "
                             f"Only .pdf and .txt files are allowed."
                })
                continue

            logger.info(f"Document upload received: {filename}")

            temp_path = None
            try:
                # Save to a temporary local file for extraction
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    upload.save(tmp.name)
                    temp_path = tmp.name
                results.append(pipeline.process_upload(temp_path, filename))
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}", exc_info=True)
                results.append({
                    "status": "failed",
                    "filename": filename,
                    "error": str(e),
                    "message": f"Failed to process {filename}: {e}"
                })
            finally:
                if temp_path:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass

        succeeded = [r for r in results if r.get("status") == "completed"]
        failed = [r for r in results if r.get("status") != "completed"]
        total_chunks = sum(r.get("chunks_created", 0) or 0 for r in succeeded)
        total_text_files = sum(r.get("text_files_created", 0) or 0 for r in succeeded)

        if not failed:
            overall = "completed"
        elif succeeded:
            overall = "partial"
        else:
            overall = "failed"

        response = {
            "status": overall,
            "files_total": len(results),
            "files_succeeded": len(succeeded),
            "files_failed": len(failed),
            "chunks_created": total_chunks,
            "text_files_created": total_text_files,
            "results": results,
            "message": (
                f"Processed {len(succeeded)} of {len(results)} file(s): "
                f"added {total_chunks} chunks and created "
                f"{total_text_files} text file(s)."
            )
        }

        status_code = 200 if overall in ("completed", "partial") else 400
        return jsonify(response), status_code

    except RequestEntityTooLarge:
        # Let the app-level 413 handler return a clean message
        raise
    except Exception as e:
        logger.error(f"Failed to process document upload: {e}", exc_info=True)
        return jsonify({
            "status": "failed",
            "error": "Document upload failed",
            "message": str(e)
        }), 500


@admin_bp.route("/uploads", methods=["GET"])
def list_uploads():
    """
    List the original uploaded documents currently stored.

    Works with both the local storage volume and S3/MinIO.

    Returns:
        JSON containing a ``files`` array of stored upload filenames.
    """
    try:
        storage = StorageService()
        files = sorted(storage.list_uploads())
        return jsonify({"files": files, "count": len(files)}), 200
    except Exception as e:
        logger.error(f"Failed to list uploads: {e}", exc_info=True)
        return jsonify({
            "error": "Failed to list uploads",
            "message": str(e)
        }), 500


@admin_bp.route("/download-pdf", methods=["GET"])
def download_pdf():
    """
    Download a stored document (defaults to the most recently configured PDF).

    Works with both the local storage volume and S3/MinIO.

    Returns:
        File stream of the requested document.
    """
    try:
        requested = request.args.get("filename", "document.pdf")
        filename = secure_filename(requested)
        logger.info(f"Document download requested: {filename}")

        storage = StorageService()
        data = storage.read_upload_bytes(filename)

        if data is None:
            logger.warning(f"Document not found in storage: {filename}")
            return jsonify({"error": f"Document '{filename}' not found"}), 404

        mimetype = "application/pdf" if filename.lower().endswith(".pdf") else "text/plain"
        return send_file(
            BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Failed to download document: {e}", exc_info=True)
        return jsonify({"error": "Failed to download document", "message": str(e)}), 500



@admin_bp.route("/run-rag-pipeline", methods=["POST"])
def run_rag_pipeline():
    """
    Trigger the RAG pipeline to process PDF and create vector database
    
    This endpoint will:
    1. Extract text from the PDF
    2. Chunk the text
    3. Gepages_processed": number,
        "message": "description"
    }
    """
    try:
        logger.info("RAG pipeline execution requested")
        
        # Get RAG pipeline and process PDF
        pipeline = get_rag_pipeline()
        result = pipeline.process_pdf()
        
        if result["status"] == "completed":
            logger.info(f"RAG pipeline completed: {result['chunks_created']} chunks created")
            return jsonify(result), 200
        else:
            logger.error(f"RAG pipeline failed: {result.get('error', 'Unknown error')}")
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in run_rag_pipeline: {e}", exc_info=True)
        return jsonify({
            "status": "failed",
            "error": "RAG pipeline failed",
            "message": str(e)
        }), 500


@admin_bp.route("/pipeline-status", methods=["GET"])
def get_pipeline_status():
    """
    Get current status of the RAG pipeline
    
    Returns:
    {
        "vector_db": {...},
        "last_execution": {...},
        "conversation_count": number,
        "status": "ready|error"
    }
    """
    try:
        logger.debug("Pipeline status requested")
        
        # Get RAG pipeline status
        pipeline = get_rag_pipeline()
        status = pipeline.get_status()
        
        logger.debug(f"Pipeline status: {status['status']}")
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}", exc_info=True)
        return jsonify({
            "status": "failed",
            "error": "RAG pipeline failed",
            "message": str(e)
        }), 500
