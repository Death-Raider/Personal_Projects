const MongoClient = require('mongodb').MongoClient;
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
    console.log(JSON.stringify({"values":temArr}));
    client.close();
  });
}
