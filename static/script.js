const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileVersion = document.getElementById("fileVersion");
const versionPanel = document.getElementById("versionPanel");
const detectedVersion = document.getElementById("detectedVersion");
const versionGrid = document.getElementById("versionGrid");
const processing = document.getElementById("processing");
const errorBox = document.getElementById("errorBox");

browseBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
        handleFile(fileInput.files[0]);
    }
});

["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, event => {
        event.preventDefault();
        dropZone.classList.add("dragover");
    });
});

["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, event => {
        event.preventDefault();
        dropZone.classList.remove("dragover");
    });
});

dropZone.addEventListener("drop", event => {
    const file = event.dataTransfer.files[0];

    if (file) {
        handleFile(file);
    }
});

async function handleFile(file) {
    hideError();

    if (!file.name.toLowerCase().endsWith(".aep")) {
        showError("Please select a valid .aep file.");
        return;
    }

    fileName.textContent = file.name;
    fileVersion.textContent = "Scanning project...";
    fileInfo.classList.remove("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/detect", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Unable to scan the file.");
        }

        fileVersion.textContent = `Detected: ${data.version_text}`;
        detectedVersion.textContent = data.version_text;

        buildVersionButtons(data.version);

        versionPanel.classList.remove("hidden");

        versionPanel.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    } catch (error) {
        showError(error.message);
        fileVersion.textContent = "Scan failed";
    }
}

function buildVersionButtons(currentVersion) {
    versionGrid.innerHTML = "";

    let count = 0;

    for (let target = currentVersion - 1; target >= 20; target--) {
        const button = document.createElement("button");
        button.className = "version-btn";

        button.innerHTML = `
            <span>DOWNGRADE TO</span>
            AE ${target}.x
        `;

        button.addEventListener("click", () => downgrade(target));

        versionGrid.appendChild(button);
        count++;
    }

    if (count === 0) {
        versionGrid.innerHTML = `
            <div class="error-box">
                This project is already at the minimum supported version.
            </div>
        `;
    }
}

async function downgrade(targetVersion) {
    const file = fileInput.files[0];

    if (!file) {
        showError("Please select an AEP file first.");
        return;
    }

    hideError();
    processing.classList.remove("hidden");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_version", targetVersion);

    try {
        const response = await fetch("/downgrade", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            let message = "Downgrade failed.";

            try {
                const data = await response.json();
                message = data.error || message;
            } catch (_) {}

            throw new Error(message);
        }

        const blob = await response.blob();

        const disposition = response.headers.get("Content-Disposition");
        let downloadName = `${file.name.replace(/\.aep$/i, "")}_AE${targetVersion}x.aep`;

        if (disposition) {
            const match = disposition.match(/filename="?([^"]+)"?/i);
            if (match) {
                downloadName = match[1];
            }
        }

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = downloadName;

        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(url);

        processing.innerHTML = `
            <div style="font-size:24px;">✓</div>
            <div>
                <strong>Downgrade completed!</strong>
                <span>Your AE ${targetVersion}.x project has been downloaded.</span>
            </div>
        `;

    } catch (error) {
        showError(error.message);
    } finally {
        setTimeout(() => {
            processing.classList.add("hidden");

            processing.innerHTML = `
                <div class="spinner"></div>
                <div>
                    <strong>Processing project...</strong>
                    <span>Please wait while your AEP file is converted.</span>
                </div>
            `;
        }, 3000);
    }
}

function showError(message) {
    errorBox.textContent = "⚠️ " + message;
    errorBox.classList.remove("hidden");
}

function hideError() {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
}
  
