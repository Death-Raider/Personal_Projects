// async function processImage(path){
//   const pixels = require('image-pixels')
//   let {data, width, height} = await pixels(path)
//
//   let local_newImg_R = [], local_newImg_G = [], local_newImg_B = [],
//   newImg_R = [], newImg_G = [], newImg_B = [];
//   for(let i = 0; i < data.length/4; i++){
//     local_newImg_R[i] = data[4*i]/255;
//     local_newImg_G[i] = data[4*i+1]/255;
//     local_newImg_B[i] = data[4*i+2]/255;
//   }
//   //formatting into correct form
//   for(let i = 0; i < local_newImg_R.length/width; i++){
//     newImg_R[i] = [];
//     newImg_G[i] = [];
//     newImg_B[i] = [];
//     for(let j = 0; j < width; j++){
//       newImg_R[i][j] = local_newImg_R[j + width*i]
//       newImg_G[i][j] = local_newImg_G[j + width*i]
//       newImg_B[i][j] = local_newImg_B[j + width*i]
//     }
//   }
//   return [newImg_R,newImg_G,newImg_B]
// }
function makeCircle(s){
  let m = Array(s).fill(0).map(e=>Array(s).fill(0).map(e=>0));
  // random indexs [i,j] for center of circle
  let t = [Math.floor(Math.random()*(s/2)+s/4),Math.floor(Math.random()*(s/2)+s/4),Math.floor(Math.random()*(s/2)+s/4)]
  t[2] = Math.min(t[0],s-t[0],t[1],s-t[1],t[2]) // gets the min radius
  if( t[2] == 0|| t[1]+t[2] >= s || t[0]+t[2] >= s ){return makeCircle(s)}
  else{
    for(let i = 0; i < s; i++)
      for(let j = 0; j < s; j++)
        if( Math.hypot(t[0]-i,t[1]-j) <= t[2] ) m[i][j] = 1
    return m
  }
}
function makeTriangle(s){
  let m = Array(s).fill(0).map(e=>Array(s).fill(0).map(e=>0));
  let t = [Math.floor(Math.random()*s),Math.floor(Math.random()*s)] // random indexs [i,j] for tip of triangle
  if(t[1] != 0 && t[1] != s-1 && t[0] != s-1){
    m[t[0]][t[1]] = 1
    for(let i = t[0], q=0; i < s; i++, q++){
      let j = t[1] - q
      if(j < 0 || j + 2*q + 1 > s) break
      for(let l = 0; l < 2*q + 1; l++) m[i][j+l] = 1
    }
  }else{ return makeTriangle(s) }
  return m
}
function drawMatrix(M,path,name){
  const {createCanvas} = require('canvas');
  const fs = require("fs")
  function Rgb(r,g,b){
    r = r.toString(16);
    g = g.toString(16);
    b = b.toString(16);
    if (r.length == 1)
      r = "0" + r;
    if (g.length == 1)
      g = "0" + g;
    if (b.length == 1)
      b = "0" + b;
    return "#" + r + g + b;
  }
  function addColor(value){
    let color,g;
    if(value == 0) color = Rgb(255,255,255)
    if(value < 0){
      g = (value < -1)?0:parseInt((value+1)*255)
      color = Rgb(g,g,255);
    }
    if(value > 0){
      g = (value > 1)?255:parseInt(value*255)
      color = Rgb(255,255-g,255-g);
    }
    return color;
  }
  const save = (canvas,path,name)=>{
    const buffer = canvas.toBuffer('image/png')
    fs.writeFileSync(`${path}/${name}.png`, buffer)
    return true
  }
  for(let l = 0; l < M.length; l++){
    let canvas = createCanvas(M[l].length, M[l][0].length)
    let ctx = canvas.getContext('2d')
    for(let k = 0; k < M[l].length; k++){
      for(let p = 0; p < M[l][0].length; p++){
        ctx.fillStyle = addColor(M[l][k][p])
        ctx.fillRect(p,k,1,1)
      }
    }
    save(canvas,path,`${name}_${l}`)
  }
}
const add = (a, b, k=1) => a instanceof Array ? a.map((c, i) => add(a[i], b[i])) : a + k*b;
function cm(c1,c2){ //complex multiply = cm
  // c1 and c2 are complex number in form [a,b] representing a+bi
  return [c1[0]*c2[0]-c1[1]*c2[1], c1[0]*c2[1]+c1[1]*c2[0]]
}
function vector_matrix(v,m){
  return m.map( e=>e.map((p,i)=>cm(p,v[i])).reduce((a,b)=>[a[0]+b[0],a[1]+b[1]]) )
}
let complex_matrix = [
  [[1,2],[1,-1]],
  [[1,1],[1,-2]]
]
/*
   1+2i   1-i
   1+i  1-2i
*/
let x = [
  Array(30).fill(0).map((e,j)=>Array(30).fill(0).map((e,i)=>(i==15?1:j==15?-1:0))),
  Array(30).fill(0).map((e,j)=>Array(30).fill(0).map((e,i)=>(i==15?1:j==15?-1:0)))
];
drawMatrix(x,"IM_x","x")
// x[complex part][real part]
let x_rotation = [
  Array(100).fill(0).map((e,j)=>Array(100).fill(0).map((e,i)=>-0.5)),
  Array(100).fill(0).map((e,j)=>Array(100).fill(0).map((e,i)=>-0.5)),
  Array(100).fill(0).map((e,j)=>Array(100).fill(0).map((e,i)=>-0.5)),
  Array(100).fill(0).map((e,j)=>Array(100).fill(0).map((e,i)=>-0.5))
]
let Z = [
  Array(150).fill(0).map((e,j,b)=>Array(150).fill(0).map((e,i,a)=>(i==a.length/2?1:j==b.length/2?-1:-0.6))),
  Array(150).fill(0).map((e,j,b)=>Array(150).fill(0).map((e,i,a)=>(i==a.length/2?1:j==b.length/2?-1:-0.6)))
]
let P = []
for(let i = -x[0].length/2 + 1; i < x[0].length/2; i++){
  for(let j = -x[0].length/2; j < x[0].length/2; j++){
    Z = [
      Array(150).fill(0).map((e,j,b)=>Array(150).fill(0).map((e,i,a)=>(i==a.length/2?1:j==b.length/2?-1:-0.6))),
      Array(150).fill(0).map((e,j,b)=>Array(150).fill(0).map((e,i,a)=>(i==a.length/2?1:j==b.length/2?-1:-0.6)))
    ]
    P[0] = cm([j,i],complex_matrix[0][0])
    P[2] = cm([j,i],complex_matrix[1][0])
    for(let b = -x[1].length/2 + 1; b < x[1].length/2; b++){
      for(let a = -x[1].length/2; a < x[1].length/2; a++){
        if(true) { // any speical conditions u wanna add
          P[1] = cm([a,b],complex_matrix[0][1])
          P[3] = cm([a,b],complex_matrix[1][1])
          for(let k = 0; k < Z.length; k++){
            let [x1_a,x1_b] = [ P[2*k][0]+x_rotation[2*k].length/2 , x_rotation[2*k].length/2-P[2*k][1] ]
            let [x2_a,x2_b] = [ P[2*k+1][0]+x_rotation[2*k+1].length/2 , x_rotation[2*k+1].length/2-P[2*k+1][1] ]
            let [z_a,z_b] = [Z[0].length/2+P[2*k][0]+P[2*k+1][0],Z[0].length/2-P[2*k][1]-P[2*k+1][1]]
            x_rotation[2*k][x1_b][x1_a] = x[0][x[0].length/2-i][x[0].length/2+j]/2
            x_rotation[2*k+1][x2_b][x2_a] = x[1][x[1].length/2-b][x[1].length/2+a]/2
            Z[k][z_b][z_a] = x[1][x[1].length/2-b][x[1].length/2+a]/2 + x[0][x[0].length/2-i][x[0].length/2+j]/2
          }
        }
      }
    }
    drawMatrix(x_rotation,"IM_y","y_"+(i+x[0].length/2-1)+","+(j+x[0].length/2) )
    drawMatrix(Z,"IM_z","z_"+(i+x[0].length/2-1)+","+(j+x[0].length/2) )
  }
}
