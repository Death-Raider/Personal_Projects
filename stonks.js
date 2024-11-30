const alpha = require('alphavantage')({ key: 'ababbaba' });//idk any keys lol
const spawn = require('child_process').spawn;

let datapoint = 0,// 1 datapoint is 'time' seconds (compressed time step)
predictTime = 1, //itterator for interval
interval = 3, //comparing interval ( compare even 5th value i.e 1 - 5, 5 - 10 , ... )
bet = 10, // the amount u r betting
returnRate = 0.8,
profits = 0,
losses = 0,
values=[];
//time > 2.88 mins <-- alphavantage min time for free trial
let time = 3*60; //refresh stock data in 'time' seconds

let data = 'DOWN';//start prediction

//loops ever 'time' seconds forever
var stock = setInterval( () => {
  (async () => {
    let pp = await f().catch(error => { console.log(error);});//pauses till the data is recieved
    values[datapoint] = parseFloat(pp);//intreprets data as float value
    console.log(values);//prints stock data
    if(datapoint == 0) sendData(data);

    //check every 'interval' position in 'values' i.e: if values[a,b,c,d,e,f,g,h,i,j,...] and interval = 2
    //then it call at every 2nd value {(c,e,g,...) starts from 3rd value as array start from 0} to the prediction.

    if(datapoint == interval*predictTime){
      //campares value of prediction with the actual data
      if(compareValue(values[datapoint],values[interval*(predictTime-1)]) == data ){
        console.log('PROFIT');//prediction correct
        profits++;//increments the profit count
      }else{
        console.log('LOSS / NO PROFIT');//prediction false
        losses++;//increments the loss count
      }

      data = prediction(2);//gets the prediction
      sendData(data);//sends the prediction to python

      var ratio = profits && losses ? profits/losses : Math.max(profits,-losses)

      console.log('profits =',profits,', losses =',losses,', profit-loss ratio =',ratio);
      console.log(`money made = ${profits*returnRate*bet - bet*losses}`);

      predictTime++;//updates the itterator for the data point calculations
    }

    console.log('prediction:',data);//print prediction
    datapoint++;//updates the compressed time step

    if (losses >= 4) quit();

  })();}, 1000 * time);


//gets the exchange rate
async function f(){
  let dataget = await alpha.forex.rate('ltc', 'usd');
  return dataget['Realtime Currency Exchange Rate']['5. Exchange Rate'];
}
//compares value of x w.r.t to y
function compareValue(x,y){
  if(x > y){
    return 'UP';
  }else if (x == y){
    return 'SAME';
  }else{
    return 'DOWN';
  }
}
//sending data
function sendData(x){
  var py = spawn('python', ['stonks2.py'])//calls the .py file

  /* dont need to recieve data

  //gets the data from the python file
  py.stdout.on('data', function(data){
    datagot = data.toString('utf8');
    console.log('data! 1',datagot);
  });

  //when the code ends, do this
  py.stdout.on('end', function(){
    console.log('data! 2',datagot);
  });

  //error
  py.stderr.on("data", function(data) {
    console.log("stderr------",data.toString('utf8'));
  });

*/

  py.stdin.write(JSON.stringify(x));//sends to python file
  py.stdin.end();
}
//exits the interval loop
function quit(x){
  clearInterval(x);
}
//gives prediction
function prediction(derivativeCount){
  let prediction = taylorSeries(derivativeCount, (values.length-1)-derivativeCount, 1,5)
  console.log(`raw prediction = ${prediction}`);
  return compareValue(prediction,values[values.length - 1]);
}

/* things for prediction aka MATH aka the GUD STUFF*/

//calculates the finite taylor series
function taylorSeries(totalSum,startsValue,timestep,variableValue){
  let sum = 0;
  for(let i = 0; i <= totalSum; i++){
    sum += derivatives(i,startsValue,timestep) * (Math.pow(variableValue,i) / factorial(i));
  }
  return sum;
}
//calculates nth derivative per start value given a timestep
function derivatives(n,startsValue,timestep){
  let sum = 0;
  if(values.length > n){
    for(let i = 0; i <= n; i++){
      sum += Math.pow(-1,i) * C(n,i) * values[startsValue + timestep*(n-i)]
    }
  }else{
    throw `not enough data points to compute ${n}th derivative`;
  }
  return sum /Math.pow(timestep,n);
}
//factorial
function factorial(n){
  return n ? n * factorial(n - 1) : 1;
}
//combination formula
function C(n,r){
  let value = factorial(n)/(factorial(r)*factorial(n-r));
  return value;
}

/*
if ya wanna plot on desmos or anywere really
a->start value
x->variable
t->data points to consider
p->taylor sum limit
n->nth derivative (for second line)
f/d are random assignments for testing.
put array of stock data insted of sine function

k\left(a,x,t,p\right)\ =\ \sum_{q=0}^{p}\frac{S\left(q,a,t\right)\left(x-a\right)^{q}}{q!}
S\left(n,x,t\right)=\frac{1}{t^{n}}\sum_{i=0}^{n}\left(\left(-1\right)^{i}C\left(n,i\right)f\left[x+t\left(n-i\right)\right]\right)
C\left(n,r\right)\ =\ \frac{n!}{r!\left(n-r\right)!}
f=\left[57.79, 57.89, 58.08,58.03, 57.89, 57.63,57.62, 57.77, 57.81,57.83, 57.86, 57.89,58.07\right]
0,0
1,1
*/
