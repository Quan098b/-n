let isLoadingZones = false;
let firstLoad = true;

async function fetchWithTimeout(url, options = {}, timeoutMs = 5000) {
    const controller = new AbortController();

    const timeoutId = setTimeout(() => {
        controller.abort();
    }, timeoutMs);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });

        return response;
    } finally {
        clearTimeout(timeoutId);
    }
}


async function loadZones(showLoading = false) {
    if (isLoadingZones) {
        return;
    }

    isLoadingZones = true;

    const container = document.getElementById("zoneContainer");

    // Chỉ hiện "Đang tải..." ở lần đầu hoặc khi bấm Làm mới.
    // Không xóa giao diện cũ khi tự cập nhật nền.
    if (showLoading || firstLoad) {
        container.innerHTML = "<p>Đang tải danh sách khu...</p>";
    }

    try {
        const res = await fetchWithTimeout("/api/zones", {}, 5000);
        const data = await res.json();

        if (!data.success) {
            if (firstLoad || showLoading) {
                container.innerHTML = "<p>Lỗi tải danh sách khu.</p>";
            }
            return;
        }

        renderZones(data.zones);
        firstLoad = false;

    } catch (err) {
        console.error("Lỗi loadZones:", err);

        // Không xóa giao diện cũ nếu chỉ là lỗi tạm thời
        if (firstLoad || showLoading) {
            container.innerHTML = `
                <p style="color:red;">
                    Lỗi kết nối API /api/zones. Kiểm tra server_app.py hoặc console terminal.
                </p>
            `;
        }

    } finally {
        isLoadingZones = false;
    }
}


function renderZones(zones) {
    const container = document.getElementById("zoneContainer");
    container.innerHTML = "";

    if (!zones || zones.length === 0) {
        container.innerHTML = "<p>Chưa có khu nào. Hãy tạo khu mới.</p>";
        return;
    }

    zones.forEach(zone => {
        const card = document.createElement("div");
        card.className = "zone-card";

        const statusText = zone.occupied ? "Đang có client" : "Trống";
        const statusClass = zone.occupied ? "busy" : "free";
        const clientText = zone.client_id ? zone.client_id : "Không có";

        card.innerHTML = `
            <div class="zone-header">
                <div>
                    <div class="zone-title">${escapeHtml(zone.name)}</div>
                    <span class="badge ${statusClass}">${statusText}</span>
                </div>
                <button class="delete-btn" onclick="deleteZone('${zone.id}')">Xóa</button>
            </div>

            <div class="zone-body">
                <img src="/stream/${zone.id}" alt="${escapeHtml(zone.name)}">
                <div class="info">
                    <div><b>Client:</b> ${escapeHtml(clientText)}</div>
                    <div><b>Thời gian:</b> ${zone.time || "Chưa có"}</div>
                    <div><b>Kích thước:</b> ${zone.width}x${zone.height}</div>
                    <div><b>Phát hiện:</b> ${zone.detections}</div>
                </div>
            </div>
        `;

        container.appendChild(card);
    });
}


async function createZone() {
    const input = document.getElementById("zoneNameInput");
    const name = input.value.trim();

    if (!name) {
        alert("Vui lòng nhập tên khu.");
        return;
    }

    try {
        const res = await fetchWithTimeout("/api/zones", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name
            })
        }, 5000);

        const data = await res.json();

        if (!data.success) {
            alert(data.message || "Không tạo được khu.");
            return;
        }

        input.value = "";
        await loadZones(true);

    } catch (err) {
        alert("Lỗi tạo khu: " + err);
    }
}


async function deleteZone(zoneId) {
    if (!confirm("Bạn có chắc muốn xóa khu này không?")) {
        return;
    }

    try {
        const res = await fetchWithTimeout(`/api/zones/${zoneId}`, {
            method: "DELETE"
        }, 5000);

        const data = await res.json();

        if (!data.success) {
            alert(data.message || "Không xóa được khu.");
            return;
        }

        await loadZones(true);

    } catch (err) {
        alert("Lỗi xóa khu: " + err);
    }
}


function escapeHtml(text) {
    if (text === null || text === undefined) {
        return "";
    }

    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// Nút Làm mới trên giao diện gọi loadZones(true)
window.loadZones = function () {
    loadZones(true);
};

window.createZone = createZone;
window.deleteZone = deleteZone;


// Lần đầu tải trang
loadZones(true);


// Tự cập nhật nền, không làm mất giao diện cũ
setInterval(() => {
    loadZones(false);
}, 5000);