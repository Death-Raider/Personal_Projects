const express = require('express');
const Datastore = require('nedb');

const app = express();
app.use(express.static('public'));
app.use(
  express.json({
    limit:'1mb',
    type:'application/json'
  })
);

const database = new Datastore('database.db');
database.loadDatabase();

app.get('/api',(request, responce) => {
  database.find({},(err,data) =>{
    if(err){
      responce.end();
      return;
    }
    responce.json(data);
  })
});

app.post('/api', (request, responce) => {
  const datagot = request.body;
  const timestamp = Date.now();
  datagot.timestamp = timestamp;
  console.log(datagot);
  database.insert(datagot);
  responce.json(datagot);
});

app.listen(process.env.PORT || 3000, () => console.log('listening at 3000'));
