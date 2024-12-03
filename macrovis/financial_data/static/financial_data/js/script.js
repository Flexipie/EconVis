// financial_data/static/financial_data/js/script.js

console.log('script.js is loaded'); // Debugging log

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

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOMContentLoaded event fired'); // Debugging log

  // Attach event listeners to indicator items
  const indicatorItems = document.querySelectorAll('.indicator-item');
  if (indicatorItems.length > 0) {
    indicatorItems.forEach(item => {
      item.addEventListener('click', handleIndicatorClick);
    });
    console.log(`Attached click event listeners to ${indicatorItems.length} indicator items.`);
  } else {
    console.error('No indicator items found.');
  }

  // Attach event listeners to country selects
  const country1Select = document.getElementById('country-select-1');
  const country2Select = document.getElementById('country-select-2');

  if (country1Select && country2Select) {
    country1Select.addEventListener('change', updateChart);
    country2Select.addEventListener('change', updateChart);
    console.log('Attached change event listeners to country selectors.');
  } else {
    console.error('Country selectors not found.');
  }

  // Attach event listener to "Save as Favorite" button
  const saveFavoriteBtn = document.getElementById('saveFavoriteBtn');
  if (saveFavoriteBtn) {
    console.log('Save Favorite button found in DOM:', saveFavoriteBtn);
    saveFavoriteBtn.addEventListener('click', saveFavorite);
  } else {
    console.error("Save Favorite button not found in DOM.");
  }

  // Initialize with first indicator
  const firstIndicator = document.querySelector('.indicator-item');
  if (firstIndicator) {
    firstIndicator.classList.add('active');
    console.log('Initialized with first indicator:', firstIndicator.dataset.indicator);
    updateChart();
  } else {
    console.error('No indicator items available to initialize.');
  }

  // Load favorites and last searches on page load
  loadFavorites();
  loadLastSearches();
});

// Create or update chart
function createOrUpdateChart(datasets, title) {
  const ctx = document.getElementById('chart').getContext('2d');

  if (chart) {
    chart.destroy();
    console.log('Existing chart destroyed.');
  }

  chart = new Chart(ctx, {
    type: 'line',
    data: { datasets: datasets },
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

  console.log('Chart created/updated with title:', title);
}

// Fetch data and update chart
async function updateChart() {
  const country1Select = document.getElementById('country-select-1');
  const country2Select = document.getElementById('country-select-2');
  const activeIndicator = document.querySelector('.indicator-item.active');

  if ((!country1Select.value && !country2Select.value) || !activeIndicator) {
    console.log('No country or indicator selected.');
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
  console.log('Selected indicator:', indicator);

  if (!indicator) {
    console.log('No indicator code found in dataset.');
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
          data: data.map(d => ({ x: d.year, y: d.value })),
          borderColor: getCountryColor(i),
          backgroundColor: 'transparent',
          fill: false,
        });
      }
    }

    if (datasets.length > 0) {
      const title = activeIndicator.textContent;
      createOrUpdateChart(datasets, title);

      // After updating the chart, record the search
      recordLastSearch(selectedCountries, indicator);
    } else {
      console.log('No data available for selected countries and indicator.');
    }
  } catch (error) {
    console.error('Error updating chart:', error);
  }
}

// Function to record last search
function recordLastSearch(selectedCountries, indicator) {
  const country1 = selectedCountries[0].code;
  const country2 = selectedCountries[1].code;

  fetch('/last-searches/add/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ country1, country2, index: indicator }),
  })
    .then(response => response.json())
    .then(data => {
      console.log('Last Search response:', data.message);
      loadLastSearches(); // Refresh the last searches list
    })
    .catch(error => console.error('Error recording last search:', error));
}

// Save favorite
function saveFavorite() {
  console.log('saveFavorite function called.');

  const country1 = document.getElementById('country-select-1').value;
  const country2 = document.getElementById('country-select-2').value;
  const indicatorElem = document.querySelector('.indicator-item.active');
  const index = indicatorElem ? indicatorElem.dataset.indicator : null;

  if (!country1 || !country2 || !index) {
    alert('Please select two countries and an indicator before saving a favorite.');
    console.log('Missing data for saving favorite.');
    return;
  }

  console.log('Saving favorite:', { country1, country2, index });

  fetch('/favorites/add/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ country1, country2, index }),
  })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data.message);
      alert(data.message);
      loadFavorites();
    })
    .catch(error => console.error('Error saving favorite:', error));
}

// Load favorites
function loadFavorites() {
  console.log('Loading favorites...');
  fetch('/favorites/list/')
    .then(response => response.json())
    .then(data => {
      console.log('Loaded favorites:', data.favorites);
      const favoritesList = document.getElementById('favoritesList');
      favoritesList.innerHTML = '';

      data.favorites.forEach(favorite => {
        const listItem = document.createElement('li');
        listItem.dataset.id = favorite.id;
        listItem.style.display = 'flex';
        listItem.style.alignItems = 'center';
        listItem.style.justifyContent = 'space-between'; // Space between name and delete button
        listItem.style.padding = '10px';
        listItem.style.borderBottom = '1px solid #ddd'; // Separator between items
        listItem.style.cursor = 'pointer'; // Indicate that the item is clickable

        const favoriteName = document.createElement('span');
        favoriteName.textContent = favorite.name;
        favoriteName.style.flex = '1'; // Take up remaining space

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.classList.add('delete-favorite-btn');
        deleteBtn.style.marginLeft = '10px';
        deleteBtn.style.color = 'red';
        deleteBtn.style.cursor = 'pointer';
        deleteBtn.style.background = 'none';
        deleteBtn.style.border = 'none';
        deleteBtn.style.fontSize = '0.9em';

        // Add click event to delete favorite
        deleteBtn.addEventListener('click', function(event) {
          event.stopPropagation();  // Prevent triggering the loadFavorite
          deleteFavorite(favorite.id, listItem);
        });

        // Append favorite name and delete button to the list item
        listItem.appendChild(favoriteName);
        listItem.appendChild(deleteBtn);

        // Add click event to load favorite comparison
        listItem.addEventListener('click', function() {
          loadFavorite(favorite.id);
        });

        favoritesList.appendChild(listItem);
      });
    })
    .catch(error => console.error('Error loading favorites:', error));
}

// Load last searches
function loadLastSearches() {
    console.log('Loading last searches...');
    fetch('/last-searches/list/')
      .then(response => response.json())
      .then(data => {
        console.log('Loaded last searches:', data.last_searches);
        const lastSearchesList = document.getElementById('lastSearchesList');
        lastSearchesList.innerHTML = '';
  
        data.last_searches.forEach((search, index) => {
          const listItem = document.createElement('li');
          listItem.dataset.id = search.id;
          listItem.classList.add('last-search-item'); // Add a class for CSS styling
  
          // Create a container for search info and date
          const searchInfo = document.createElement('span');
          searchInfo.textContent = `${index + 1}. ${search.name}`; // Add numbering
          searchInfo.classList.add('search-info'); // Add a class for CSS styling
  
          const searchDate = document.createElement('span');
          searchDate.textContent = search.date;
          searchDate.classList.add('search-date'); // Add a class for CSS styling
  
          // Append search info and date to the list item
          listItem.appendChild(searchInfo);
          listItem.appendChild(searchDate);
  
          // Add click event to load search comparison
          listItem.addEventListener('click', function() {
            loadFavorite(search.id);
          });
  
          lastSearchesList.appendChild(listItem);
        });
      })
      .catch(error => console.error('Error loading last searches:', error));
  }

// Delete favorite
function deleteFavorite(favoriteId, listItem) {
  console.log(`Deleting favorite with ID: ${favoriteId}`);

  // Add confirmation dialog
  const confirmDelete = confirm('Are you sure you want to delete this favorite?');
  if (!confirmDelete) {
    console.log('Favorite deletion canceled.');
    return;
  }

  fetch(`/favorites/delete/${favoriteId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({}),  // Empty body, as server only needs the favorite_id from URL
  })
    .then(response => response.json())
    .then(data => {
      console.log('Delete response:', data.message);
      if (data.message === 'Favorite deleted successfully') {
        // Remove the list item from the DOM
        listItem.remove();
        alert('Favorite deleted successfully.');
      } else {
        alert('Error deleting favorite: ' + data.message);
      }
    })
    .catch(error => console.error('Error deleting favorite:', error));
}

// Load favorite and update graph
function loadFavorite(favoriteId) {
  console.log(`Loading favorite with ID: ${favoriteId}`);
  fetch(`/favorites/load/${favoriteId}/`)
    .then(response => response.json())
    .then(data => {
      console.log('Loaded favorite data:', data);
      document.getElementById('country-select-1').value = data.country1;
      document.getElementById('country-select-2').value = data.country2;
      const indicatorElem = document.querySelector(`[data-indicator="${data.index}"]`);
      if (indicatorElem) {
        indicatorElem.click();
      } else {
        console.error(`Indicator with code ${data.index} not found.`);
      }
    })
    .catch(error => console.error('Error loading favorite:', error));
}

// Get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}