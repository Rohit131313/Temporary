const BASE_URL = "http://localhost:5000";
// const BASE_URL = "https://c0a7-2409-40c4-4-35bc-99d5-3443-fb5d-1cf6.ngrok-free.app";
let currentStudentId = null;
let selectedDate = null;


async function loadAttendance() {
    const batch = document.getElementById("batch").value;
    const branch = document.getElementById("branch").value;
    selectedDate = document.getElementById("datePicker").value;

    const res = await fetch(`${BASE_URL}/get-attendance`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ batch,branch,selectedDate })
        });
    const students = await res.json();
    console.log("Fetched students:", students);

    const tbody = document.querySelector("#attendanceTable tbody");
    tbody.innerHTML = "";

    students.forEach(student => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${student.id}</td>
            <td>${student.name}</td>
            <td onclick="openModal('${student.id}', '${student.name}', '${student.attendance || "Attendance not marked"}', '${student.remark || "No remark"}')">
                ${student.attendance || "Attendance not marked"}
            </td>
            <td onclick="openModal('${student.id}', '${student.name}', '${student.attendance || "Attendance not marked"}', '${student.remark || "No remark"}')">
                ${student.remark || "No remark"}
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function openModal(id, name, attendance, remark) {
    currentStudentId = id;
    document.getElementById("modalStudentName").textContent = name;
    document.getElementById("modalStatus").value = attendance.toLowerCase();
    document.getElementById("modalRemark").value = remark === "No remark" ? "" : remark;

    document.getElementById("modal").style.display = "block";
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}

async function submitModal() {
    const status = document.getElementById("modalStatus").value;
    const remark = document.getElementById("modalRemark").value;

    await fetch(`${BASE_URL}/admin/update-attendance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: currentStudentId, date: selectedDate, status, remark })
    });

    closeModal();
    loadAttendance(); // Refresh table
}

async function markHolidayForAll() {
    const date = document.getElementById("datePicker").value;
    await fetch(`${BASE_URL}/admin/mark-holiday`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date })
    });
    loadAttendance(); 
}

function downloadCSV() {
    const table = document.getElementById("attendanceTable");
    let csv = [];

    for (let row of table.rows) {
        let cols = Array.from(row.cells).map(col => {
            const input = col.querySelector("input, textarea");
            if (input) {
                return `"${input.value}"`;
            } else {
                return `"${col.textContent.trim()}"`;
            }
        });
        csv.push(cols.join(","));
    }

    const blob = new Blob([csv.join("\n")], { type: "text/csv" });
    const link = document.createElement("a");
    link.download = `attendance_${selectedDate}.csv`;
    link.href = URL.createObjectURL(blob);
    link.click();
}

async function exportExcelWithDateRange() {
    const start = new Date(document.getElementById("startDate").value);
    const end = new Date(document.getElementById("endDate").value);
    if (isNaN(start) || isNaN(end) || start > end) {
        alert("Invalid date range");
        return;
    }

    // Prepare list of dates
    const dateList = [];
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        dateList.push(new Date(d).toISOString().split('T')[0]);
    }

    // Fetch data
    const res = await fetch('/getAllStudentsData');
    const students = await res.json(); // { scholarNo: { name, attendance, remarks }, ... }

    // Construct array of arrays (AOA) for Excel sheet
    const aoa = [];
    const header = ["Scholar No", "Name", ...dateList];
    aoa.push(header);

    for (const [id, data] of Object.entries(students)) {
        const row = [id, data.name || '-'];
        for (const date of dateList) {
            const status = data.attendance?.[date];
            if (status === "present") row.push("present");
            else if (status === "absent") row.push("absent");
            else if (status === "holiday") row.push("holiday");
            else row.push("not marked");
        }
        aoa.push(row);
    }

    // Create worksheet and set column widths
    const ws = XLSX.utils.aoa_to_sheet(aoa);
    ws['!cols'] = aoa[0].map(() => ({ wch: 15 })); // Optional: fixed column width for better spacing

    // Create and download workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Attendance");
    XLSX.writeFile(wb, `attendance_${document.getElementById("startDate").value}_to_${document.getElementById("endDate").value}.xlsx`);
}

async function loadCalendar() {
    const studentid = document.getElementById("studentid").value;
    const res = await fetch(`${BASE_URL}/getStudentData`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ studentid })
    });
    const data = await res.json();
    const attendance = data.attendance;
    const remarks = data.remarks;
    console.log(attendance)
    renderAttendanceCalendar(attendance,remarks)
}

function renderAttendanceCalendar(attendanceData, remarkData = {}) {
    const events = [];

    console.log(remarkData)
    for (const [date, status] of Object.entries(attendanceData)) {
        let color;

        if (remarkData[date] && remarkData[date].trim() !== "") {
            color = "blue"; // Special color for dates with remarks
        } else {
            switch (status) {
                case "present":
                    color = "green";
                    break;
                case "absent":
                    color = "red";
                    break;
                case "leave":
                    color = "yellow";
                    break;
                default:
                    color = "gray";
            }
        }
        let statusStr = String(status);
        events.push({
            title: statusStr.charAt(0).toUpperCase() + statusStr.slice(1),
            start: date,
            color: color
        });
    }

    const calendarEl = document.getElementById("calendar");
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        events: events,
        height: "auto",   // Automatically adjust height
        contentHeight: 350, // Set max height to compress
        aspectRatio: 2,  
        headerToolbar: {
            left: "prev,next",
            center: "title",
            right: ""
        }
    });

    calendar.render();
}

