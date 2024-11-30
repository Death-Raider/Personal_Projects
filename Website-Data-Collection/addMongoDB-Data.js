const fs = require('fs');
const MongoClient = require('mongodb').MongoClient;
const data = JSON.parse(fs.readFileSync(0))

//mongodbUser:                     User       password
const connection = 'mongodb+srv://key'
var mongo;
var db;

MongoClient.connect(connection,{useUnifiedTopology: true},(err, client) => {
  if (err) return console.error(err);
  db = client.db('ImageDataStore');//the location of "collection" in mongodb
  mongo = db.collection('train');//collection
  sendValues(client)
});

async function sendValues(client){
  await mongo.insertOne({'_id':genRandId(9),'value':Buffer.from(data.arr,'utf8'),'Digit':data.dig});
  console.log('{"Database_Update":"Success"}');
  client.close();
}

function genRandId(idLen){
  let idArray = ['abcdefghijklmnopqrstuvwqyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ','0123456789','@#$%^&*()~|{}[]_-=+/.,;:<>'];
  let idLength = idLen;
  let id = ''
  for(let i = 0; i < idLength; i++){
    let chosen = idArray[rand(0,4)]
    id += (chosen.length == 26)? chosen[rand(0,26)]: chosen[rand(0,10)]
  }
  function rand(a,b){
    return Math.floor(Math.random()*(b-a) + a)
  }
  return id;
}
