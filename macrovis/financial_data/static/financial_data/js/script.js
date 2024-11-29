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
document.querySelectorAll('.indicator-item').forEach(item => {
    item.addEventListener('click', handleIndicatorClick);
});

// Add change event listeners to country selects
document.getElementById('country-select-1').addEventListener('change', updateChart);
document.getElementById('country-select-2').addEventListener('change', updateChart);

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
            title: {
                display: true,
                text: title
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
    const datasets = [];

    try {
        for (const country of selectedCountries) {
            const response = await fetch(`/api/data/${country.code}/${indicator}/`);
            if (!response.ok) {
                console.error(`Error fetching data for ${country.code}: ${response.statusText}`);
                continue;
            }
            
            const data = await response.json();
            
            if (Array.isArray(data) && data.length > 0) {
                const processedData = data.map(item => ({
                    x: item.year,
                    y: item.value
                })).filter(item => item.y !== null);

                datasets.push({
                    label: country.name,
                    data: processedData,
                    borderColor: getCountryColor(selectedCountries.indexOf(country)),
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4,
                    spanGaps: true
                });
            }
        }

        if (datasets.length > 0) {
            createOrUpdateChart(datasets, activeIndicator.textContent);
            document.getElementById('indicator-info').textContent = 
                `Showing ${activeIndicator.textContent} for ${selectedCountries.map(c => c.name).join(' and ')}`;
        } else {
            document.getElementById('indicator-info').textContent = 'No data available for selected countries';
        }
    } catch (error) {
        console.error('Error updating chart:', error);
        document.getElementById('indicator-info').textContent = 'Error loading data';
    }
}

// Initialize with first indicator
document.querySelector('.indicator-item').classList.add('active');
updateChart();