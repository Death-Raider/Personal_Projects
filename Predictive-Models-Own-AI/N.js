const fs = require('fs');
const data = JSON.parse(fs.readFileSync(0));
const {NeuralNetwork} = require('@death-raider/Neural-Network')

let network = new NeuralNetwork({
  input_nodes : 96,
  layer_count : [20,5,20],
  output_nodes : 96,
  weight_bias_initilization_range : [-1,1]
});

network.Activation.hidden = [(x)=>Math.tanh(x),(x)=>1-Math.tanh(x)*Math.tanh(x)];

function img(){
  let output = new Array(10).fill(0)
  let randomImg = Math.floor(Math.random()*data.length)
  let input = data[randomImg][0].slice()
  // output[data[randomImg][1]] = 1;
  return [input,input]
}
network.train({
  TotalTrain : 2e+6,
  batch_train : 2,
  trainFunc : img,
  TotalVal : 1000,
  batch_val : 2,
  validationFunc : img,
  learning_rate : 0.1
});

// (async () =>{
//   await network.load('imageClassifier') //make sure network is of correct structure
//   console.log({
//     use:network.use(
//       [
//         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
//         1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,
//         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
//         0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0,
//         0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1,
//         1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0,
//         0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0,
//         0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0
//       ]
//     ),
//     model:network
//   });
// })()

// should be 2 or [0,0,1,0,0,0,0,0,0,0,0]
console.log(JSON.stringify({
  use:network.use(
    [
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
      1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,
      0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
      0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0,
      0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1,
      1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0,
      0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0,
      0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]
  ),
  model:network
}));
