//require
const express = require('express');
const fs = require('fs');

//uses the files present in folder public
const app = express();
app.use(express.static('public'));

//sets max JSON get request size
app.use(
  express.json({
    limit:'1kb',
    type:'application/json'
  })
);

app.post('/apiPost', async (request,responce) => {
  const dataGot = request.body;
  const dataRaw = JSON.parse(fs.readFileSync(`newData/${dataGot.val}.txt`).toString("utf8"));
  responce.send(JSON.stringify(dataRaw))
});

app.listen(process.env.PORT || 3000, () => console.log('listening at 3000'));
