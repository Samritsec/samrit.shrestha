document.addEventListener("DOMContentLoaded", () => {
  /* ====== Live Uptime ====== */
  const elUptime = document.getElementById("kpi-uptime");
  const t0 = Date.now();
  setInterval(() => {
    const s = Math.floor((Date.now() - t0) / 1000);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    if (elUptime)
      elUptime.textContent = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  }, 1000);

  /* ====== Chart.js Setup (with Bar Chart) ====== */
  const dataObj = window.DASHBOARD_DATA || {};
  const threats = dataObj.threats || [];
  const cpu = dataObj.cpu || [];
  const mem = dataObj.mem || [];
  const statusCounts = dataObj.statusCounts || { online: 0, offline: 0, unusual: 0 };

  function makeLineChart(el, data, color, threshold) {
    const ctx = document.getElementById(el);
    if (!ctx || !data.length) return;
    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map((_, i) => i + 1),
        datasets: [
          {
            data,
            borderColor: color,
            backgroundColor: color + "22",
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2
          },
          threshold
            ? {
                data: Array(data.length).fill(threshold),
                borderColor: "#ff5555",
                borderDash: [5, 5],
                pointRadius: 0,
                borderWidth: 1.5,
                fill: false
              }
            : {}
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { display: false },
          y: { ticks: { color: "#8ca3b5" }, grid: { color: "rgba(140,163,181,0.1)" } }
        }
      }
    });
  }

  makeLineChart("chartThreats", threats, "#63e2ff");
  makeLineChart("chartCPU", cpu, "#64ffb1", 85);
  makeLineChart("chartMEM", mem, "#ffa94d", 85);

  // ===== Replaced Status Split: Bar Chart =====
  const ctxStatus = document.getElementById("chartStatus");
  if (ctxStatus) {
    new Chart(ctxStatus, {
      type: "bar",
      data: {
        labels: ["Online", "Offline", "Unusual"],
        datasets: [
          {
            label: "Device States",
            data: [statusCounts.online, statusCounts.offline, statusCounts.unusual],
            backgroundColor: ["#10b981cc", "#ef4444cc", "#f59e0bcc"],
            borderColor: ["#10b981", "#ef4444", "#f59e0b"],
            borderWidth: 1.5,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true }
        },
        scales: {
          x: {
            ticks: { color: "#8ca3b5" },
            grid: { display: false }
          },
          y: {
            beginAtZero: true,
            ticks: { color: "#8ca3b5" },
            grid: { color: "rgba(140,163,181,0.1)" }
          }
        }
      }
    });
  }

  /* ====== Modal Helpers ====== */
  const openModal = id => document.getElementById(id).setAttribute("aria-hidden", "false");
  const closeModal = id => document.getElementById(id).setAttribute("aria-hidden", "true");

  /* ====== View Heavy (Sample Data) ====== */
  const btnCpu = document.getElementById("btnViewCpuHeavy");
  const btnMem = document.getElementById("btnViewMemHeavy");
  const heavyClose = document.getElementById("heavyClose");
  const heavyBody = document.getElementById("heavyTableBody");
  const heavyCount = document.getElementById("heavyCount");

  function loadSampleHeavy() {
    heavyBody.innerHTML = "";
    const sample = [
      { hostname: "server-01", os: "Ubuntu 22.04", ip: "192.168.1.45", status: "online", cpu: 92, mem: 81, last_seen: "2025-10-22 19:10 UTC" },
      { hostname: "gateway-04", os: "Windows 11", ip: "192.168.1.73", status: "offline", cpu: 88, mem: 90, last_seen: "2025-10-22 17:46 UTC" },
      { hostname: "laptop-05", os: "macOS 14", ip: "192.168.1.105", status: "online", cpu: 95, mem: 87, last_seen: "2025-10-22 18:20 UTC" }
    ];
    sample.forEach(d => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${d.hostname}</td>
        <td>${d.os}</td>
        <td>${d.ip}</td>
        <td>${d.status === "online" ? '<span class="pill pill-ok">Online</span>' : '<span class="pill pill-bad">Offline</span>'}</td>
        <td>${d.cpu}%</td>
        <td>${d.mem}%</td>
        <td>${d.last_seen}</td>`;
      heavyBody.appendChild(tr);
    });
    heavyCount.textContent = `${sample.length} device(s) above threshold (CPU or Memory ≥ 85%)`;
    openModal("heavyModal");
  }
  if (btnCpu) btnCpu.onclick = loadSampleHeavy;
  if (btnMem) btnMem.onclick = loadSampleHeavy;
  if (heavyClose) heavyClose.onclick = () => closeModal("heavyModal");

  /* ====== At-Risk History (Sample Data) ====== */
  const btnViewAtRisk = document.getElementById("btnViewAtRisk");
  const modalRisk = document.getElementById("atRiskModal");
  const riskClose = document.getElementById("atRiskClose");
  const riskTable = document.getElementById("atRiskTableBody");

  function loadSampleRisk() {
    const sample = [
      { date: "2025-10-21 14:32 UTC", hostname: "server-12", issue: "Brute Force Login", severity: "Critical", mitigation: "Reset admin credentials" },
      { date: "2025-10-21 13:45 UTC", hostname: "gateway-04", issue: "Malware Flag", severity: "High", mitigation: "Isolate endpoint & scan" },
      { date: "2025-10-20 22:11 UTC", hostname: "workstation-07", issue: "Suspicious Login", severity: "Medium", mitigation: "Monitor user sessions" }
    ];
    riskTable.innerHTML = "";
    sample.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.date}</td>
        <td>${r.hostname}</td>
        <td>${r.issue}</td>
        <td><span class="pill ${
          r.severity === "Critical"
            ? "pill-bad"
            : r.severity === "High"
            ? "pill-warn"
            : "pill-ok"
        }">${r.severity}</span></td>
        <td>${r.mitigation}</td>`;
      riskTable.appendChild(tr);
    });
    openModal("atRiskModal");
  }
  if (btnViewAtRisk) btnViewAtRisk.onclick = loadSampleRisk;
  if (riskClose) riskClose.onclick = () => closeModal("atRiskModal");

  /* ====== Theme Toggle ====== */
  const toggle = document.createElement("div");
  toggle.className = "theme-toggle";
  toggle.innerHTML = "🌗";
  document.body.appendChild(toggle);
  toggle.onclick = () => {
    document.documentElement.classList.toggle("light");
    localStorage.setItem("theme", document.documentElement.classList.contains("light") ? "light" : "dark");
  };
  if (localStorage.getItem("theme") === "light") document.documentElement.classList.add("light");
});
