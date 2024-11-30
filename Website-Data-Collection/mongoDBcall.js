const MongoClient = require('mongodb').MongoClient;
const fs = require('fs')

//mongodbUser:                     User       password
const connection = 'mongodb+srv://key'
var mongo,db;

MongoClient.connect(connection,{useUnifiedTopology: true},(err, client) => {
  if (err) return console.error(err);
  db = client.db('ImageDataStore');//the location of "collection" in mongodb
  mongo = db.collection('train');//collection
  ready(client)
});

function ready(client,x){
  mongo.find().toArray().then(result => {
    let temArr = [];
    let data = {};

    for(let i = 0; i < result.length; i++){
      temArr[i] = [];
      temArr[i][0] = [];
      for(let byt of result[i].value.buffer.values()){
        temArr[i][0].push(byt)
      }
      temArr[i][1] = result[i].Digit;
    }
    client.close();
    meta(temArr)
  });
}

async function meta(mongoValues){
  const input = JSON.parse(fs.readFileSync(0)).values;

  outputArray = [];
  for(let i = 0; i < mongoValues.length; i++) outputArray[i] = [];

  mongoValues.forEach((array, index1) => {
    array[0].forEach((item, index2) => {
      outputArray[index1][index2] = input[index2] - item;
    });
  });

  let a = percentage(input);
  let values = [];
  outputArray.forEach((item, i) => {
    values.push(percentage(item));
  });

  minval = getMinMax(values);

  sentMessage = {};

  if(a > 14 && a < 55 ){
    if(minval.min < 16){
      let num;
      mongoValues.forEach((array, index1) => {
        if(index1 == minval.index_min){
          num = array[1]
        }
      });
      sentMessage = {
        message:`the digit is weekly calssified as ${num}`,
        value:true
      }
    }else{
      sentMessage.message = "Not a digit";
      sentMessage.value = false;
    }
  }else{
    sentMessage.message = "data not sufficient or too much data";
    sentMessage.value = false;
  }

  console.log(JSON.stringify(sentMessage));
}

function percentage(arr){
  let pp = arr.filter( (item) => {return item == 1 || item == -1 } )
  return((pp.length/arr.length)*100);
}
function getMinMax(x){
  let min = x[0], max = x[0];

  for (let i = 1, len=x.length; i < len; i++) {
    let v = x[i];
    min = (v < min) ? v : min; // it means if(v < min){min = v;}else{min = min;}
    max = (v > max) ? v : max; // it means if(v > max){max = v;}else{max = max;}
  }
  return {min:min,index_min:x.indexOf(min),max:max,index_max:x.indexOf(max)};
}
