const spawn = require('child_process').spawn;
const express = require('express');
const app = express();

//uses the files present in folder public
app.use(express.static('public'));
//sets max JSON get request size
app.use(
  express.json({
    limit:'1kb',
    type:'application/json'
  })
);

//the submission of data to mongodb
app.post('/submitData', async (request,responce) => {

  const datagot = request.body;//gets the content submitted
  console.log("Dataset Enter val ->",datagot);//show content

  //waits for promise resolve in validation
  const check = await validation(datagot);

  //updates status
  var status = {"Database_Update":check.reasonError};
  //addes the user data to the database if the validation passes
  if(check.validation){
    //creates promise for call of the file
    const updateDatabasePromise = new Promise( (resolve,reject) => {
      callFile('addMongoDB-Data.js',JSON.stringify({'arr':datagot.values,'dig':parseInt(datagot.digit)}),resolve,reject)
    });
    //gets status about the update of the database
    status = await updateDatabasePromise;
  }

  console.log(status,check.validation);
  //sends the status
  responce.send(JSON.stringify(status))
});

//to get the prediction from the NN that was called
app.get('/prediction',(request, responce) => {
  console.log("request got");
  responce.send('{"output":"not enough Data, wait till enough data has been submitted"}');
});

app.listen(process.env.PORT || 3000, () => console.log('listening at 3000'));


async function validation(input){
  try{
    let length_test,digit_value_test,string_test, meta_test = true;//validations to pass
    string_test = input.digit != null && input.digit.toString().length == 1;//tests for string value
    digit_value_test = (string_test)? !isNaN(parseInt(input.digit)) : false;//tests digit
    length_test = input.values.length == 96;//tests input length

    //gives reason based on tests
    reason = (!string_test)?"missing Digit or illegal Digit value":( (!digit_value_test)?"Digit is not a number":(!length_test)?"illegal drawing":"pass" );
    //calles for the weak digit classifier if all the other test pass
    if(string_test && digit_value_test && length_test){
      //creates a promise for the file's return
      const callMetaValidationPromise = new Promise( (resolve,reject) => {
        callFile('mongoDBcall.js',JSON.stringify(input),resolve,reject)
      });
      //stores responce
      const responceValidation = await callMetaValidationPromise;

      //updates reason and sets value to the digit test
      reason = responceValidation.message;
      meta_test = responceValidation.value;
    }
    console.log("criteria->",string_test,digit_value_test,length_test,meta_test);
    //returns the end result (did the data send? if not then why)
    let sending = {
      validation:(string_test && digit_value_test && length_test && meta_test)?true:false,
      reasonError: reason
    }
    return sending;
  }catch(e){
    let sending = {
      validation: false,
      reasonError: "DB failure"
    }
    return sending;
  }
}

function callFile(filePath,sendData = JSON.stringify({"val":1}),resolve,reject){
  const test = spawn('node',[filePath]);
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
