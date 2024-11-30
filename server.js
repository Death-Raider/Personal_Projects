
const express = require('express');
const MongoClient = require('mongodb').MongoClient;
const app = express();

app.use(express.static('public'));
app.use(
  express.json({
    limit:'1mb',
    type:'application/json'
  })
);

const connection = ''
var PL;
var db;

MongoClient.connect(connection,{useUnifiedTopology: true},(err, client) => {
  if (err) return console.error(err);
  console.log('Connected to Database');
  db = client.db('Test');
  PL = db.collection('problemsLocation');
});

app.post('/prob', (request, responce) => {
  const datagot = request.body;
  if(datagot.lat != undefined){
    console.log("undefined location");
    const timestamp = Date.now();
    datagot.timestamp = timestamp;
    PL.insertOne(datagot).then(result => {
      responce.json("Results logged");
    });
  }
  else{
    responce.json("Undefined location")
  }
});

app.get('/datastore',(request,responce) => {
  db.collection('problemsLocation').find().toArray().then(result => {
    responce.json(result);
  });
});

app.listen(process.env.PORT || 2000, () => console.log('listening at 2000'));
