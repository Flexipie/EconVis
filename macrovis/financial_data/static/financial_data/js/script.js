// Initialize chart
let chart = null;

// Function to get a color based on index
function getCountryColor(index) {
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
    return colors[index % colors.length];
}

// Handle indicator click
function handleIndicatorClick(event) {
    const indicator = event.currentTarget;
    const indicatorCode = indicator.getAttribute('data-code');
    
    if (!indicatorCode) {
        console.error('No indicator code found');
        return;
    }

    // Remove active class from all indicators
    document.querySelectorAll('.indicator-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to clicked indicator
    indicator.classList.add('active');

    // Update chart
    updateChart();
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the main comparison page
    const indicatorList = document.querySelector('.indicator-list');
    if (!indicatorList) return; // Exit if we're not on the main page

    // Add click event listeners to indicators
    document.querySelectorAll('.indicator-item').forEach(item => {
        item.addEventListener('click', handleIndicatorClick);
    });

    // Add change event listeners to country selects
    const countrySelect1 = document.getElementById('country-select-1');
    const countrySelect2 = document.getElementById('country-select-2');
    
    if (countrySelect1 && countrySelect2) {
        countrySelect1.addEventListener('change', updateChart);
        countrySelect2.addEventListener('change', updateChart);
    }

    // Initialize with first indicator
    const firstIndicator = document.querySelector('.indicator-item');
    if (firstIndicator) {
        firstIndicator.classList.add('active');
        updateChart();
    }
});

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

// Hide error message
function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// Fetch data and update chart
async function updateChart() {
    hideError();
    
    const activeIndicator = document.querySelector('.indicator-item.active');
    const country1 = document.getElementById('country-select-1')?.value;
    const country2 = document.getElementById('country-select-2')?.value;
    
    if (!activeIndicator) {
        showError('Please select an indicator');
        return;
    }

    if (!country1 || !country2) {
        showError('Please select both countries');
        return;
    }

    const indicatorCode = activeIndicator.getAttribute('data-code');
    if (!indicatorCode) {
        showError('Invalid indicator selected');
        return;
    }

    console.log('Selected indicator:', indicatorCode);

    try {
        const datasets = [];
        
        // Fetch data for first country
        console.log(`Fetching data for country: ${country1}, indicator: ${indicatorCode}`);
        const response1 = await fetch(`/data/${country1}/${indicatorCode}/`);
        if (!response1.ok) {
            throw new Error(`Error fetching data for ${country1}`);
        }
        const data1 = await response1.json();
        if (data1.values && data1.values.length > 0) {
            datasets.push({
                label: data1.country,
                data: data1.values,
                borderColor: getCountryColor(0),
                fill: false
            });
        }

        // Fetch data for second country
        console.log(`Fetching data for country: ${country2}, indicator: ${indicatorCode}`);
        const response2 = await fetch(`/data/${country2}/${indicatorCode}/`);
        if (!response2.ok) {
            throw new Error(`Error fetching data for ${country2}`);
        }
        const data2 = await response2.json();
        if (data2.values && data2.values.length > 0) {
            datasets.push({
                label: data2.country,
                data: data2.values,
                borderColor: getCountryColor(1),
                fill: false
            });
        }

        if (datasets.length > 0) {
            createOrUpdateChart(datasets, activeIndicator.textContent.trim());
        } else {
            showError('No data available for the selected countries and indicator');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Error loading data. Please try different selections.');
        
        // Clear the chart if there's an error
        if (chart) {
            chart.destroy();
            chart = null;
        }
    }
}

// Create or update chart
function createOrUpdateChart(datasets, title) {
    const ctx = document.getElementById('chart').getContext('2d');
    
    if (chart) {
        chart.destroy();
    }

    const years = [...new Set(datasets.flatMap(ds => ds.data.map(d => d.year)))].sort();
    
    const formattedDatasets = datasets.map(ds => ({
        ...ds,
        data: years.map(year => {
            const point = ds.data.find(d => d.year === year);
            return point ? point.value : null;
        })
    }));

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: formattedDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
}