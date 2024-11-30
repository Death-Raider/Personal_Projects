var spawn = require('child_process').spawn;
const express = require('express');
const app = express();


app.use(express.static('public'));
app.use(
  express.json({
    limit:'1mb',
    type:'application/json'
  })
);
app.post('/trainingData', (request, responce) => {
  const datagot = request.body;
  console.log(datagot.values);
  dataWithTrain(datagot.values)
  responce.end()
});
app.get('/prediction',(request, responce) => {
  console.log("request got");
  testOutput = [ // Output from trained AI model
    [0.1,0.1,0.1,0.1,0.1,0.9,0,0,0,0]
  ]
  data = {
    output: getMax(testOutput[0])
  }
  responce.json(data)
});

app.listen(process.env.PORT || 3000, () => console.log('listening at 3000'));


function dataWithTrain(){
  var datagen = spawn('python', ['datasetForm.py'])//calls the .py file
  //calles for data generation
  datagen.stdin.write(JSON.stringify('generate'));//sends to python file
  datagen.stdin.end();
  //when the code ends do this
  datagen.stdout.on('end',function(){
    print("Dataset Generated")
  });
  //error
  datagen.stderr.on("data", function(data) {
    console.log("stderr------",data.toString('utf8'));
  });
}

function getMax(x){
  let min = x[0], max = x[0];

  for (let i = 1, len=x.length; i < len; i++) {
    let v = x[i];
    min = (v < min) ? v : min; // it means if(v < min){min = v;}else{min = min;}
    max = (v > max) ? v : max; // it means if(v > max){max = v;}else{max = max;}
  }
  return x.indexOf(max);
}
function createImgOfData(x){
  var imgCreate = spawn('python',['createImg.py']);

  imgCreate.stdin.write(JSON.stringify(x))
  imgCreate.stdin.end();

  imgCreate.stderr.on("data", function(data) {
    console.log("stderr------",data.toString('utf8'));
  });
}