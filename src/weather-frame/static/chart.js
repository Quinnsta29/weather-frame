function createHourlyChart(hourlyData, currentHourIndex) {
  const endIndex = currentHourIndex + 21;

  const selectedTimes = hourlyData.time.slice(currentHourIndex, endIndex);
  const temperatures = hourlyData.temperature_2m.slice(currentHourIndex, endIndex);
  const rainfall = hourlyData.rain.slice(currentHourIndex, endIndex);

  const timeLabels = selectedTimes.map(time => {
    const date = new Date(time);
    return date.getHours() + ':00';
  });

  const ctx = document.getElementById('hourlyChart').getContext('2d');
  const hourlyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timeLabels,
      datasets: [
        {
          label: 'Temperatuur (°C)',
          data: temperatures,
          borderColor: '#ff6b35',
          backgroundColor: 'transparent',
          borderWidth: 2,
          tension: 0.2,
          pointRadius: 0,
          yAxisID: 'y'
        },
        {
          label: 'Neerslag (mm)',
          data: rainfall,
          borderColor: '#3498db',
          backgroundColor: 'transparent',
          borderWidth: 2,
          tension: 0.2,
          pointRadius: 0,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: false,
      maintainAspectRatio: false,
      animation: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      scales: {
        x: {
          display: true,
          ticks: {
            callback: function(value, index, ticks){
              return index % 4 === 0 ? this.getLabelForValue(value) : '';
            }
          },
          grid: {
            display: false,
          }
        },
        y: {
          type: 'linear',
          display: false,
          position: 'left',
          title: {
            display: true,
            text: 'Temperature (°C)'
          },
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            callback: function(value, index, ticks) {
              const min = Math.min(...temperatures);
              const max = Math.max(...temperatures);
              if (value === min || value === max) {
                return String(value) + ' °C';
              }
              return '';
            }
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            display: true,
            callback: function(value, index, ticks) {
              const min = Math.min(...rainfall);
              const max = Math.max(...rainfall);
              if (value === min || value === max) {
                return value.toFixed(1) + ' mm';
              }
              return '';
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
        ctx.font = '12px Arial';
        ctx.fillStyle = '#ff6b35';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';

        dataset.data.forEach((value, index) => {
          if (index > 0 && index < dataset.data.length - 1 && index % 3 === 0) {
            const point = meta.data[index];
            const x = point.x;
            const y = point.y - 5;
            
            ctx.fillText(value.toFixed(1) + '°', x, y);
          }
        });
        
        ctx.restore();
      }
    }]
  });

  return hourlyChart;
}