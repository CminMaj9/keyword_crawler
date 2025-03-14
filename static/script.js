// static/script.js
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

// 添加/更新词包
async function addWordPackage() {
    const packageName = document.getElementById("package-name").value.trim();
    const wordsText = document.getElementById("package-words").value.trim();
    if (!packageName || !wordsText) {
        alert("请输入词包名称和关键词");
        return;
    }
    const words = wordsText.split(",").map(w => w.trim());
    try {
        const response = await fetch("/api/word-packages", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ package_name: packageName, words: words })
        });
        const data = await response.json();
        alert(data.message);
        loadWordPackages();
    } catch (error) {
        alert("添加词包失败");
    }
}

// 加载词包列表
async function loadWordPackages() {
    const response = await fetch("/api/word-packages");
    const packages = await response.json();
    const list = document.getElementById("word-package-list");
    const select = document.getElementById("fetch-package");
    const fetchButton = document.getElementById("fetch-button");
    list.innerHTML = "";
    select.innerHTML = '<option value="">请选择词包</option>';

    let firstPackage = null;
    for (const [name, words] of Object.entries(packages)) {
        if (!firstPackage) firstPackage = name;
        const li = document.createElement("li");
        li.textContent = `${name}: ${words.join(", ")}`;
        list.appendChild(li);
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        select.appendChild(option);
    }

    if (firstPackage) {
        select.value = firstPackage;  // 默认选中第一个词包
        fetchButton.disabled = false;
        console.log("默认选中词包:", firstPackage);  // 调试信息
    } else {
        select.value = "";  // 确保默认值为空
        fetchButton.disabled = true;
        list.innerHTML = '<li style="color: #d63031;">暂无词包，请先添加</li>';
        console.log("无词包可用，禁用拉取按钮");
    }
}

// 手动拉取数据
async function manualFetch() {
    const button = document.getElementById("fetch-button");
    const progressBar = document.getElementById("progress");
    const select = document.getElementById("fetch-package");
    const packageName = select.value;

    // 调试信息
    console.log("选择的词包:", packageName);
    if (!packageName || packageName === "") {
        alert("请选择一个词包");
        return;
    }

    button.disabled = true;
    let progress = 0;
    progressBar.style.width = `${progress}%`;
    progressBar.innerText = `${progress}%`;

    try {
        const response = await fetch("/api/fetch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ package_name: packageName })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "拉取失败");
        }

        const data = await response.json();
        alert(data.message);
        loadLogs();
        progressBar.style.width = "100%";
        progressBar.innerText = "100%";
    } catch (error) {
        console.error("拉取失败:", error);
        alert(`拉取失败：${error.message}，请查看日志`);
        loadLogs();
    } finally {
        button.disabled = false;
    }
}

// 获取当天记录
async function fetchDailyRecords() {
    const messageElement = document.getElementById("daily-records-message");
    const tbody = document.getElementById("daily-records-body");
    tbody.innerHTML = "";
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
                    <td>${record.package}</td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        let errorMessage = "获取当天记录失败";
        if (error instanceof Response) {
            const errorData = await error.json();
            errorMessage = errorData.detail || errorMessage;
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
    loadWordPackages();
    setInterval(checkCookieStatus, 600000);
});