function createHourlyChart(hourlyData, currentHourIndex) {
  const endIndex = currentHourIndex + 21;

  const selectedTimes = hourlyData.time.slice(currentHourIndex, endIndex);
  const temperatures = hourlyData.temperature_2m.slice(currentHourIndex, endIndex);
  const rainfall = hourlyData.rain.slice(currentHourIndex, endIndex);

  // Simplify data - show fewer points for cleaner display
  const timeLabels = selectedTimes.map(time => {
    const date = new Date(time);
    return date.getHours() + ':00';
  });

  const ctx = document.getElementById('hourlyChart').getContext('2d');

  const dpr = window.devicePixelRatio || 2; // Use at least 2x for crispness
  const canvas = ctx.canvas;
  canvas.style.width = "100%";
  canvas.style.height = "200px";
  canvas.width = canvas.offsetWidth * dpr;
  canvas.height = canvas.offsetHeight * dpr;
  ctx.scale(dpr, dpr);
  const hourlyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timeLabels,
      datasets: [
        {
          label: 'Temperatuur (°C)',
          data: temperatures,
          borderColor: '#f37106ff', // Black for better contrast on e-ink
          backgroundColor: 'transparent',
          borderWidth: 6, // Increased thickness for visibility
          tension: 0.2,
          pointRadius: 0, // Add visible points
          pointStyle: 'circle',
          yAxisID: 'y'
        },
        {
          label: 'Neerslag (mm)',
          data: rainfall,
          borderColor: '#0067ddff', // Dark gray for contrast
          backgroundColor: 'transparent',
          borderWidth: 5, // Thicker line
          tension: 0.1,
          pointRadius: 0, // Add visible points
          pointStyle: 'rect', // Different point shape to distinguish from temperature
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: false,
      maintainAspectRatio: false,
      animation: false,
      layout: {
        padding: {
          top: 30,
          right: 10,
          left: 25,
          bottom: 60
        }
      },
      interaction: {
        mode: 'index',
        intersect: false,
      },
      scales: {
        x: {
          display: true,
          ticks: {
            callback: function(value, index, ticks){
              return index % 3 === 0 ? this.getLabelForValue(value) : ''; // Show fewer x-axis labels
            },
            font: {
              size: 16, // Larger font
              weight: 'bold' // Bold for better visibility
            },
            color: '#000000', // Black for contrast
            maxRotation: 0, // Force horizontal labels
            minRotation: 0, // Ensure they don't rotate at all
          },
          grid: {
            display: false,
          }
        },
        y: {
          type: 'linear',
          display: false, // Changed to true for better readability
          position: 'left',
          title: {
            display: true,
            text: '°C',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          grid: {
            color: '#cccccc', // Light gray grid
            lineWidth: 1,
            drawOnChartArea: true, // Add horizontal grid lines
          },
          ticks: {
            font: {
              size: 16,
              weight: 'bold'
            },
            color: '#000000',
            callback: function(value, index, ticks) {
              // Show more y-axis labels for temperature
              return String(value) + '°';
            }
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          min: 0, // Force minimum to always be 0
          suggestedMax: 2, // Suggest reasonable maximum for rainfall
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            display: true,
            font: {
              size: 20,
              weight: 'bold'
            },
            color: '#000000',
            callback: function(value, index, ticks) {
              // Show all rainfall values with mm
              return value.toFixed(1) + ' mm';
            },
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
        title: {
          display: false
        },
      },
    },
    plugins: [{
      id: 'temperatureLabels',
      afterDatasetsDraw: function(chart) {
        const ctx = chart.ctx;
        const dataset = chart.data.datasets[0];
        const meta = chart.getDatasetMeta(0);
        
        ctx.save();
        ctx.font = 'bold 22px Arial'; // Larger, bolder font
        ctx.fillStyle = '#000000'; // Black for contrast
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';

        dataset.data.forEach((value, index) => {
          // Show temperature at key points (every 3 hours)
          if (index % 3 === 0) {
            const point = meta.data[index];
            const x = point.x;
            const y = point.y - 12; // More space above point
            
            ctx.fillText(value.toFixed(1) + '°', x, y);
          }
        });
        
        ctx.restore();
      }
    }]
  });

  return hourlyChart;
}