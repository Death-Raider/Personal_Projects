var data = {};
var hold;
parseImg()
setInterval(() => {getData()},1000 * 5)//gets the data every 5 sec
function parseImg(){
  var grid = [];
  boxGridX.forEach((item, i) => {
    grid.push([boxGridX[i],boxGridY[i]])
  });
  grid = grid.map(JSON.stringify).reverse().filter(function (e, i, a) {
    return a.indexOf(e, i+1) === -1;
  }).reverse().map(JSON.parse);
  let dataRaw = new Array(12);
  // dataRaw.forEach((dataItem, dataIndex) => {
  //   grid.forEach( (gridItem, gridIndex) => {if(gridItem[1] == dataIndex) dataItem[gridItem[0]] = 1; });
  // });
  data.values = [];
  for(let y = 0; y < dataRaw.length; y++){
    dataRaw[y] = new Array(8);
    dataRaw[y].fill(0);
    for(let g = 0; g < grid.length; g++){
      if(grid[g][1] == y){
        dataRaw[y][grid[g][0]] = 1;
      }
    }
    data.values = data.values.concat(dataRaw[y])
  }
  sendData();
}
function sendData(){
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data) //converts to json the data to send
  };
  responceServer();
  //sends data and logs the responce
  async function responceServer(){
    const responce = await fetch('/trainingData',options);//sends to '/trainingData'
    //const jsonget = await responce.json(); //parses responce json file
  }
}
async function getData(){
  const responce = await fetch('/prediction')//requests from '/'
  const jsonget = await responce.json()//parses the json
  if( hold != jsonget.output){
    document.getElementById('prediction').innerHTML = jsonget.output;
  }
  hold = jsonget.output;
}
