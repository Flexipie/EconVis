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
        const queryParams = new URLSearchParams();

        // Process form data to handle multiple country selections
        for (let [key, value] of formData.entries()) {
            if (key === 'countries[]') {
                queryParams.append('countries[]', value);
            } else {
                queryParams.append(key, value);
            }
        }
        
        try {
            const response = await fetch(`/api/filter/?${queryParams.toString()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
                return;
            }

            if (!data.data || data.data.length === 0) {
                showError('No data available for the selected criteria');
                return;
            }

            updateChart(data.data);
            updateTable(data.data);
        } catch (error) {
            console.error('Error:', error);
            showError('An error occurred while fetching the data. Please try again.');
        }
    }

    function showError(message) {
        const errorDiv = document.getElementById('error-message') || 
            document.createElement('div');
        errorDiv.id = 'error-message';
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const chartContainer = document.getElementById('chartContainer');
        if (!document.getElementById('error-message')) {
            chartContainer.appendChild(errorDiv);
        }
    }

    function updateChart(data) {
        const ctx = document.getElementById('dataChart').getContext('2d');
        
        if (chart) {
            chart.destroy();
        }

        const chartData = prepareChartData(data);
        
        chart = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Financial Data Visualization',
                        font: {
                            size: 16
                        }
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Value'
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

    function prepareChartData(data) {
        const years = [...new Set(data.map(item => item.year))].sort();
        const countries = [...new Set(data.map(item => item.country))];
        
        const datasets = countries.map((country, index) => {
            const countryData = data.filter(item => item.country === country);
            return {
                label: country,
                data: years.map(year => {
                    const point = countryData.find(item => item.year === year);
                    return point ? point.value : null;
                }),
                borderColor: getColor(index),
                backgroundColor: getColor(index, 0.1),
                borderWidth: 2,
                fill: false,
                tension: 0.4
            };
        });

        return {
            labels: years,
            datasets: datasets
        };
    }

    function getColor(index, alpha = 1) {
        const colors = [
            '#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f',
            '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'
        ];
        const color = colors[index % colors.length];
        
        if (alpha !== 1) {
            return color + Math.round(alpha * 255).toString(16).padStart(2, '0');
        }
        return color;
    }

    function updateTable(data) {
        const tableDiv = document.getElementById('dataTable');
        const years = [...new Set(data.map(item => item.year))].sort();
        const countries = [...new Set(data.map(item => item.country))];

        let html = '<table><thead><tr><th>Year</th>';
        countries.forEach(country => {
            html += `<th>${country}</th>`;
        });
        html += '</tr></thead><tbody>';

        years.forEach(year => {
            html += `<tr><td>${year}</td>`;
            countries.forEach(country => {
                const point = data.find(item => item.year === year && item.country === country);
                html += `<td>${point ? point.value.toFixed(2) : '-'}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        tableDiv.innerHTML = html;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAdvancedFilters);
