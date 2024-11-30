// Initialize chart
let chart = null;

// Function to get a color based on index
function getCountryColor(index) {
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
    return colors[index % colors.length];
}

// Handle indicator click
function handleIndicatorClick(event) {
    // Remove active class from all indicators
    document.querySelectorAll('.indicator-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to clicked indicator
    event.currentTarget.classList.add('active');

    // Update chart
    updateChart();
}

// Add click event listeners to indicators
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.indicator-item').forEach(item => {
        item.addEventListener('click', handleIndicatorClick);
    });

    // Add change event listeners to country selects
    document.getElementById('country-select-1').addEventListener('change', updateChart);
    document.getElementById('country-select-2').addEventListener('change', updateChart);

    // Initialize with first indicator
    const firstIndicator = document.querySelector('.indicator-item');
    if (firstIndicator) {
        firstIndicator.classList.add('active');
        updateChart();
    }
});

// Create or update chart
function createOrUpdateChart(datasets, title) {
    const ctx = document.getElementById('chart').getContext('2d');
    
    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Year'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Value'
                    }
                }
            }
        }
    });
}

// Fetch data and update chart
async function updateChart() {
    const country1Select = document.getElementById('country-select-1');
    const country2Select = document.getElementById('country-select-2');
    const activeIndicator = document.querySelector('.indicator-item.active');
    
    if ((!country1Select.value && !country2Select.value) || !activeIndicator) {
        console.log('No country or indicator selected');
        return;
    }

    const selectedCountries = [
        { 
            code: country1Select.value, 
            name: country1Select.options[country1Select.selectedIndex]?.text 
        },
        { 
            code: country2Select.value, 
            name: country2Select.options[country2Select.selectedIndex]?.text 
        }
    ].filter(country => country.code);

    const indicator = activeIndicator.dataset.indicator;
    console.log('Selected indicator:', indicator); // Debug log
    
    if (!indicator) {
        console.log('No indicator code found in dataset');
        return;
    }

    const datasets = [];

    try {
        for (let i = 0; i < selectedCountries.length; i++) {
            const country = selectedCountries[i];
            console.log(`Fetching data for country: ${country.code}, indicator: ${indicator}`);
            
            const response = await fetch(`/api/financial-data/${country.code}/${indicator}/`);
            
            if (!response.ok) {
                console.error(`Error fetching data for ${country.code}: ${response.statusText}`);
                continue;
            }
            
            const data = await response.json();
            console.log(`Received data for ${country.code}:`, data);
            
            if (data && Array.isArray(data)) {
                datasets.push({
                    label: country.name,
                    data: data.map(d => ({x: d.year, y: d.value})),
                    borderColor: getCountryColor(i),
                    backgroundColor: 'transparent',
                    fill: false
                });
            }
        }

        if (datasets.length > 0) {
            const title = activeIndicator.textContent;
            createOrUpdateChart(datasets, title);
        } else {
            console.log('No data available for the selected countries and indicator');
        }
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}