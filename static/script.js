// 检查 Cookies 状态
async function checkCookieStatus() {
    const response = await fetch("/api/cookies/status");
    const data = await response.json();
    document.getElementById("cookie-status").innerText = `${data.message} (状态: ${data.status})`;
    document.getElementById("cookie-status").className = data.status === "valid" ? "success" : "failed";
}

// 更新 Cookies
async function updateCookies() {
    const cookieInput = document.getElementById("cookie-input").value.trim();
    if (!cookieInput) {
        alert("请输入 Cookies");
        return;
    }

    try {
        const response = await fetch("/api/cookies/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cookies: cookieInput })
        });
        const data = await response.json();
        alert(data.message);
        checkCookieStatus();
    } catch (error) {
        alert("更新 Cookies 失败，请检查输入格式");
    }
}

// 手动拉取数据
async function manualFetch() {
    const button = document.getElementById("fetch-button");
    button.disabled = true;
    const progressBar = document.getElementById("progress");

    let progress = 0;
    progressBar.style.width = `${progress}%`;
    progressBar.innerText = `${progress}%`;

    const interval = setInterval(async () => {
        const response = await fetch("/api/progress");
        const data = await response.json();
        progress = data.progress;
        progressBar.style.width = `${progress}%`;
        progressBar.innerText = `${progress}%`;

        if (progress >= 100) {
            clearInterval(interval);
            button.disabled = false;
        }
    }, 500);

    try {
        const response = await fetch("/api/fetch", { method: "POST" });
        const data = await response.json();
        alert(data.message);
        loadLogs();
    } catch (error) {
        alert("拉取失败，请查看日志");
        loadLogs();
    } finally {
        progressBar.style.width = "100%";
        progressBar.innerText = "100%";
        clearInterval(interval);
        button.disabled = false;
    }
}

// 获取当天记录
async function fetchDailyRecords() {
    const messageElement = document.getElementById("daily-records-message");
    const tbody = document.getElementById("daily-records-body");
    tbody.innerHTML = ""; // 清空表格

    try {
        const response = await fetch("/api/daily-records");
        const data = await response.json();
        messageElement.innerText = data.message;
        messageElement.className = "success";

        if (data.data && data.data.length > 0) {
            data.data.forEach(record => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${record.date}</td>
                    <td>${record.keyword}</td>
                    <td>${record.monthpv}</td>
                    <td>${record.bid}</td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        let errorMessage = "获取当天记录失败";
        if (error instanceof Response) {
            const errorData = await error.json();
            errorMessage = errorData.detail || errorMessage;
        } else {
            errorMessage = error.message || errorMessage;
        }
        messageElement.innerText = errorMessage;
        messageElement.className = "failed";
    }
}

// 加载日志
async function loadLogs() {
    const response = await fetch("/api/logs");
    const logs = await response.json();
    const tbody = document.getElementById("log-body");
    tbody.innerHTML = "";
    logs.forEach(log => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${log.date}</td>
            <td class="${log.status}">${log.status}</td>
            <td>${log.message}</td>
            <td>${log.timestamp}</td>
        `;
        tbody.appendChild(row);
    });
}

// 页面加载时执行
document.addEventListener("DOMContentLoaded", () => {
    checkCookieStatus();
    loadLogs();
    setInterval(checkCookieStatus, 600000);     // 每10分钟检查一次（600000ms）
});