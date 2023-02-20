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
  borderWidth: 2,
  elements: {
    point: {
      radius: 1
    }
  },
  scales: {
    x: {
      type: 'time',
      time: {
          unit: 'day'
      },
      offset: true,
      parser: function(date) {
        return date.toLocaleSTring();
      }
    },
    y: {
      beginAtZero: false
    }
  }
}
};

// render init block
const myChart = new Chart(document.getElementById('myChart'),config);