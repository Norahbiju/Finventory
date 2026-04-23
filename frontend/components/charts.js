// Ensure Chart.js is loaded via CDN in the HTML before calling these functions

let incomeExpenseChartInstance = null;
let inventoryChartInstance = null;

window.renderIncomeExpenseChart = function(canvasId, transactions) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Group transactions by Date (last 7 days or just simply by date)
    // For simplicity, we'll aggregate all transactions into Income and Expense totals
    // If you want a line chart over time, we need to sort and group by date
    
    // Create a map of dates to { income, expense }
    const dateMap = {};
    
    // Sort transactions by date ascending
    const sortedTx = [...transactions].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    
    sortedTx.forEach(tx => {
        // Just take the date part YYYY-MM-DD
        const dateStr = new Date(tx.created_at).toISOString().split('T')[0];
        if (!dateMap[dateStr]) {
            dateMap[dateStr] = { income: 0, expense: 0 };
        }
        if (tx.type === 'income') dateMap[dateStr].income += tx.amount;
        if (tx.type === 'expense') dateMap[dateStr].expense += tx.amount;
    });

    const labels = Object.keys(dateMap);
    const incomeData = labels.map(date => dateMap[date].income);
    const expenseData = labels.map(date => dateMap[date].expense);

    if (incomeExpenseChartInstance) {
        incomeExpenseChartInstance.destroy();
    }

    incomeExpenseChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Income',
                    data: incomeData,
                    borderColor: '#10b981', // Tailwind green-500
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Expenses',
                    data: expenseData,
                    borderColor: '#ef4444', // Tailwind red-500
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', align: 'end', labels: { usePointStyle: true, boxWidth: 6 } }
            },
            scales: {
                y: { beginAtZero: true, grid: { borderDash: [4, 4] } },
                x: { grid: { display: false } }
            },
            interaction: {
                mode: 'index',
                intersect: false,
            }
        }
    });
};

window.renderInventoryChart = function(canvasId, products) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Sort by stock level ascending (show lowest stock first)
    const sortedProducts = [...products].sort((a, b) => a.stock - b.stock).slice(0, 10); // Top 10 lowest

    const labels = sortedProducts.map(p => p.name.length > 15 ? p.name.substring(0,15)+'...' : p.name);
    const data = sortedProducts.map(p => p.stock);
    
    // Color code based on stock
    const bgColors = data.map(stock => stock < 10 ? '#ef4444' : (stock < 30 ? '#f59e0b' : '#6366f1'));

    if (inventoryChartInstance) {
        inventoryChartInstance.destroy();
    }

    inventoryChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Stock Level',
                data: data,
                backgroundColor: bgColors,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, grid: { borderDash: [4, 4] } },
                x: { grid: { display: false } }
            }
        }
    });
};
