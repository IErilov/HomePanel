
async function loadOverview() {
    const response = await fetch("/stats/overview");

    if (!response.ok) {
        throw new Error("Failed to load statistics");
    }

    const data = await response.json();

    document.getElementById("total-events").textContent = data.total_events ?? 0;
    document.getElementById("uploads").textContent = data.uploads ?? 0;
    document.getElementById("downloads").textContent = data.downloads ?? 0;
    document.getElementById("failed").textContent = data.failed ?? 0;
}

async function loadEvents() {
    const type = document.getElementById("event-type").value;
    const status = document.getElementById("event-status").value;

    const params = new URLSearchParams({
        limit: "50",
        offset: "0"
    });

    if (type) params.append("event_type", type);
    if (status) params.append("status", status);

    const response = await fetch(`/events/?${params}`);

    if (!response.ok) {
        throw new Error("Failed to load events");
    }

    const events = await response.json();
    const tbody = document.getElementById("events-table");

    tbody.replaceChildren();

    if (!events.length) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 6;
        cell.textContent = "No events found";
        return;
    }

    for (const event of events) {
        const row = tbody.insertRow();

        const values = [
            event.id,
            event.event_type,
            event.user_id,
            event.bucket_id,
            event.status,
            event.created_at
        ];

        for (const value of values) {
            const cell = row.insertCell();
            cell.textContent = value ?? "—";
        }
    }
}

async function initDashboard() {
    try {
        await Promise.all([
            loadOverview(),
            loadEvents()
        ]);
    } catch (error) {
        console.error(error);
    }
}

initDashboard();
