//use   $ node --max-old-space-size=5120 parsedData.js
const fs = require('fs')

//read data and filter by line break
var dataRaw = fs.readFileSync("gddrg.asc").toString("utf8")
dataRaw = dataRaw.split("\r\n");
dataRaw.pop()

//get the information about data and the data in raw form
console.log("data filtering");
let basicData = dataRaw.filter((str)=>{return (str.length<50)?true:false});
let dataValues = dataRaw.filter((str)=>{return (str.length>50)?true:false});

//cleaning the information about data
console.log("basic data filtering");
basicData.forEach((val,i,a)=>{
  let newVal = val.split(" ").filter( (elem)=>{return (elem == "")?false:true}).reverse()
  newVal.pop()
  a[i] = parseFloat(newVal[0]);
});

console.log("cleaning data got");
//makes dataValues more "workable"
dataValues = dataValues.map(e=>e.split(" ").filter(x=>(x=="")?false:true).map(x=>(x == basicData[5])?-1:parseFloat(x)) )

//create matrix
console.log("matrix creation");
let dataMatrix = new Array(basicData[1]).fill(0);
dataMatrix.forEach((e,i,a)=>{
  a[i] = new Array(basicData[0]).fill(0)
});

//update the matrix with the values
console.log("updating Matrix");
for(let i = basicData[1]-1; i >= 0; i--){
  for(let index = 0; index < basicData[0]; index++){
    let updatelat = basicData[3]+ basicData[4]*i;
    let updatelong = basicData[2]+basicData[4]*index;
    dataMatrix[i][index]=[ dataValues[i][index],[updatelong, updatelat] ];
  }
}

console.log("final sorting");
//sorting the datamatrix into clean chunks based on the frequency
let cleanData = [null,[],[],[],[],[],[],[],[],[],[]]//dont ask why.... i am desperate
for (let i = 0; i < dataMatrix.length; i++) {
  for (let j = 0; j < dataMatrix[i].length; j++) {
    if(dataMatrix[i][j][0] != -1){
      cleanData[ dataMatrix[i][j][0] ].push(dataMatrix[i][j][1])
    }
  }
}
console.log("creating new datafiles");
streams(cleanData);

function streams(cd){
  for(let j = 1; j < 11; j++){
    const stream = fs.createWriteStream(`newData/${j}.txt`);
    stream.once('open', function(fd) {
      let dataSendingStream = JSON.stringify(cd[j]);
      stream.write(dataSendingStream);
      console.log("stream",j);
      console.log(`DONE!!! stream ${j}`);
      stream.end();
    });
  }
}
