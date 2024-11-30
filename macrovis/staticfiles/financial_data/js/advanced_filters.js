// Advanced Filters JavaScript

function initializeAdvancedFilters() {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) return;

    let chart = null;

    filterForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await fetchAndUpdateData();
    });

    async function fetchAndUpdateData() {
        const formData = new FormData(filterForm);
        const queryParams = new URLSearchParams(formData);
        
        try {
            const response = await fetch(`/financial-data/api/filter/?${queryParams.toString()}`);
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
                return;
            }

            updateChart(data.data);
            updateTable(data.data);
        } catch (error) {
            console.error('Error:', error);
            showError('An error occurred while fetching the data');
        }
    }

    function showError(message) {
        alert(message);
    }

    function updateChart(data) {
        if (chart) {
            chart.destroy();
        }

        const chartData = prepareChartData(data);
        createChart(chartData);
    }

    function prepareChartData(data) {
        const labels = [...new Set(data.map(item => item.year))].sort();
        const datasets = [];

        // Group data by country
        const countryGroups = {};
        data.forEach(item => {
            if (!countryGroups[item.country__name]) {
                countryGroups[item.country__name] = [];
            }
            countryGroups[item.country__name].push({
                year: item.year,
                value: item.value
            });
        });

        // Create dataset for each country with random colors
        Object.entries(countryGroups).forEach(([country, values], index) => {
            const color = getRandomColor();
            datasets.push({
                label: country,
                data: values.map(v => v.value),
                borderColor: color,
                backgroundColor: color + '33',
                fill: false,
                tension: 0.1
            });
        });

        return { labels, datasets };
    }

    function createChart(chartData) {
        const ctx = document.getElementById('dataChart').getContext('2d');
        chart = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Financial Data Visualization'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    function updateTable(data) {
        const table = document.getElementById('dataTable');
        
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Country</th>
                        <th>Year</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(item => `
                        <tr>
                            <td>${item.country__name}</td>
                            <td>${item.year}</td>
                            <td>${item.value?.toFixed(2) ?? 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        table.innerHTML = html;
    }

    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAdvancedFilters);
