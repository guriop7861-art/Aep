import os
import tempfile
import shutil
import threading
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB

MIN_AE_VERSION = 20
MAX_AE_VERSION = 33


def cleanup_temp_dir_later(temp_dir: str, delay_seconds: int = 300):
    """Deletes a temporary AEP processing folder after the requested delay."""
    def cleanup():
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    timer = threading.Timer(delay_seconds, cleanup)
    timer.daemon = True
    timer.start()


def detect_ae_version(file_path: str):
    """Scans the AEP file header to detect the current AE version."""
    try:
        with open(file_path, "rb") as f:
            content = f.read(64)

        if len(content) < 52:
            return "Unknown (file too small)", 0

        major_version_byte = content[33]
        min_version_byte = 0x5B + (MIN_AE_VERSION - 20)
        max_version_byte = 0x5B + (MAX_AE_VERSION - 20)

        if min_version_byte <= major_version_byte <= max_version_byte:
            version = major_version_byte - 0x5B + 20
            return f"AE {version}.x", version

        return "Unknown version", 0
    except Exception as e:
        return f"Error: {str(e)}", 0


def downgrade_aep_file(input_path: str, output_path: str, target_version_num: int):
    """Modifies the AEP header chunk to convert it to the target version."""
    with open(input_path, "rb") as f:
        content = bytearray(f.read())

    if len(content) < 52:
        raise Exception("File too small to be a valid .aep file")

    current_head1 = content[33]
    target_head1 = 0x5B + (target_version_num - 20)

    if current_head1 == target_head1:
        raise Exception("The file is already in the selected target version!")

    content[33] = target_head1

    with open(output_path, "wb") as f:
        f.write(content)

    return True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    uploaded = request.files.get("file")

    if not uploaded or not uploaded.filename:
        return jsonify({"success": False, "error": "Please select an AEP file."}), 400

    if not uploaded.filename.lower().endswith(".aep"):
        return jsonify({"success": False, "error": "Only .aep files are supported."}), 400

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, Path(uploaded.filename).name)

    try:
        uploaded.save(input_path)
        ver_str, ver_num = detect_ae_version(input_path)

        if ver_num == 0:
            return jsonify({"success": False, "error": ver_str}), 400

        return jsonify({
            "success": True,
            "version": ver_num,
            "version_text": ver_str,
            "filename": uploaded.filename,
            "temp_dir": temp_dir
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/downgrade", methods=["POST"])
def downgrade():
    uploaded = request.files.get("file")
    target = request.form.get("target_version", type=int)

    if not uploaded or not uploaded.filename:
        return jsonify({"success": False, "error": "Please select an AEP file."}), 400

    if not uploaded.filename.lower().endswith(".aep"):
        return jsonify({"success": False, "error": "Only .aep files are supported."}), 400

    if target is None or target < MIN_AE_VERSION or target > MAX_AE_VERSION:
        return jsonify({"success": False, "error": "Invalid target version."}), 400

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, Path(uploaded.filename).name)
    output_name = f"{Path(uploaded.filename).stem}_AE{target}x.aep"
    output_path = os.path.join(temp_dir, output_name)

    try:
        uploaded.save(input_path)

        _, current_version = detect_ae_version(input_path)

        if current_version == 0:
            return jsonify({
                "success": False,
                "error": "The uploaded file does not appear to be a valid AEP project."
            }), 400

        if target >= current_version:
            return jsonify({
                "success": False,
                "error": "Target version must be lower than the current AE version."
            }), 400

        downgrade_aep_file(input_path, output_path, target)

        response = send_file(
            output_path,
            as_attachment=True,
            download_name=output_name,
            mimetype="application/octet-stream"
        )

        # Keep the uploaded/converted files available for 5 minutes,
        # then automatically remove the complete temporary folder.
        response.call_on_close(
            lambda: cleanup_temp_dir_later(temp_dir, 300)
        )

        return response

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(413)
def too_large(_):
    return jsonify({
        "success": False,
        "error": "File is too large. Maximum size is 500 MB."
    }), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
