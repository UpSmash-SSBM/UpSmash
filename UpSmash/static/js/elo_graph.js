// setup 
const data = {
datasets: [{
  label: 'ELO',
  data: datapoints,
}]
};
// config 
const config = {
type: 'line',
data,
options: {
  maintainAspectRatio: false,
  responsive: true,
  scales: {
    x: {
      type: 'time',
      time: {
          unit: 'day'
      },
      offset: true
    },
    y: {
      beginAtZero: true
    }
  }
}
};

// render init block
const myChart = new Chart(document.getElementById('myChart'),config);