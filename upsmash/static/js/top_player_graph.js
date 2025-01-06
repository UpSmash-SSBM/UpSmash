// setup 

// config 
const config = {
type: 'line',
data,
options: {
  maintainAspectRatio: false,
  legend: {
    position: "right",
  },
  scales: {
    x: {
      type: 'time',
      time: {
          unit: 'day'
      },
      offset: true
    },
  }
}
};

// render init block
const myChart = new Chart(document.getElementById('myChart'),config);