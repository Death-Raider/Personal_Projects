var data = {};

function parseImg(x = undefined){
  data.digit = document.getElementById('digit').value;
  document.getElementById('submitData').disabled = true;
  document.getElementById('predictor').disabled = true;
  var grid = [];//create grid
  //fills grid with x and y coordinates of boxes
  boxGridX.forEach((item, i) => {
    grid.push([boxGridX[i],boxGridY[i]])
  });
  //Removes all common array in the grid array
  grid = grid.map(JSON.stringify).reverse().filter(function (e, i, a) {
    return a.indexOf(e, i+1) === -1;
  }).reverse().map(JSON.parse);

  let dataRaw = new Array(12);//creates an array of size of height of img to create (12px)

  data.values = [];//initilizes an empty array in object data called values
  //converts the drawin image into array were each drawn white square represents a 1 and rest 0
  for(let y = 0; y < dataRaw.length; y++){//itterates over the height (y coordinates)
    dataRaw[y] = new Array(8);//creats another array for width
    dataRaw[y].fill(0);//fills x axis with 0's
    for(let g = 0; g < grid.length; g++){
      //checks y coordinate in grid and if it matches with the y coordinate level then mark 1 in x axis array
      if(grid[g][1] == y){
        dataRaw[y][grid[g][0]] = 1;
      }
    }
    //joining individual row array (x-axis) 'column' number of times to get full image array
    data.values = data.values.concat(dataRaw[y])
  }

  if(x!= undefined) sendData(x);

}

function sendData(x){
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data) //converts to json the data to send
  };
  responceServer(x);
  //sends data and logs the responce
  async function responceServer(location){
    alert("sending request, please wait")
    if(x == '/submitData'){
      const responce = await fetch(location,options);
      let status = await responce.json();
      alert(status.Database_Update)
      document.getElementById('submitData').disabled = false;
      document.getElementById('predictor').disabled = false;
    }
    if(x =='/prediction') getData(x);
  }
}
async function getData(x){
  const responce = await fetch(x)//requests from x
  const jsonget = await responce.json()
  alert("Request passed, Check prediction ")
  document.getElementById('submitDataBlock').style.display = 'none';
  document.getElementById('prediction').style.display = 'block';
  document.getElementById('prediction').innerHTML = jsonget.output.toString('utf8');
  document.getElementById('submitData').disabled = false;
  document.getElementById('predictor').disabled = false;
}
