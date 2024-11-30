const spawn = require('child_process').spawn;

const callDataSetPromise = new Promise( (resolve,reject) => {
  callFile('node','mongoDBcall.js',undefined,resolve,reject)
});

(async () => {

  const HOLY_FUCK_ALL_THE_DATA = await callDataSetPromise//get values in huge af array
  console.log("databse values ->",[HOLY_FUCK_ALL_THE_DATA.values]);
  console.log("database Values got!");

  const imgfile = new Promise((resolve,reject)=>{
    callFile('python','createImg.py',JSON.stringify(HOLY_FUCK_ALL_THE_DATA.values),resolve,reject)
  });
  const trainNN = new Promise((resolve,reject)=>{
    callFile('node','N.js',JSON.stringify(HOLY_FUCK_ALL_THE_DATA.values),resolve,reject)
  });
  const responceNN = await trainNN;
  console.log("Neural Network return -> ",responceNN.model,responceNN.use)

  const pythonResponce = await imgfile;
  console.log("python created database");
})()

function callFile(open,filePath,sendData = 'no Data',resolve,reject){
  const test = spawn(open,[filePath]);
  let x;

  test.stdin.write(sendData);
  test.stdin.end();

  test.stdout.on('data',(data) =>{
    x = JSON.parse(data.toString('utf8'));
  });
  test.stdout.on('end',()=>{
    resolve(x)
  });
  test.stderr.on('error',(err)=>{
    console.log(err);
    reject(err)
  });
}
/*
()=>{ return(
  [
    [
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
      1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,
      0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
      0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0,
      0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1,
      1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0,
      0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0,
      0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ],2
  ]
)}
*/
