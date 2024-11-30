const { createCanvas } = require('canvas')
const fs = require('fs')

plot(Y,{x:0.5,y:0.5},0.01,25)

function Y(x){ //Ordinary Differential Equation
  const get_y_2 = (y_1,x,y) => (-y*y_1-y_1**2 )
  let y_0 = -1,//initial condition
  y_1_0 = 1,//initial condition
  y=y_0,
  y_1 = y_1_0,
  dx = x >= 0?0.001:-0.001;
  for(let i = 0; Math.abs(i)<Math.abs(x); i+= dx){
    y_2 = get_y_2(y_1,i,y) //gets second derivative value
    y += y_1*dx // updates value of function
    y_1 += y_2*dx // updates value of derivative of function
  }
  return y
}
function z(x){ // normal function
  return Math.exp(-(x**2))
}
function plot(f,r,res,space){// f->functiMon, r->graph ratio , res->resolution , space->spacing between tickmarks
  const canvas = createCanvas(500, 400)
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = "white";
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  plane(canvas,ctx,{r,spacing:space})
  ctx.beginPath()
  for(let i = -parseInt(canvas.width*r.y/space),j=0; i < parseInt(canvas.width*(1-r.y)/space); i+=res,j++){
    if(f(i) <= canvas.height*r.x/space && f(i) >= -canvas.height*(1-r.x)/space){
      if(j==0)ctx.moveTo(canvas.width*r.y+i*space,canvas.height*r.x-f(i)*space)
      else{ctx.lineTo(canvas.width*r.y+i*space,canvas.height*r.x-f(i)*space)}
    }
    ctx.stroke()
    save(canvas)
  }
//   let dx = 0.007
//   let x = 0, y = -0;
//   let Ri = 0; Rj = 1
//   for(let t = 0; t < 10; t+=dx){
//     // for runner
//     Ri = 1*Math.cos(t*3)+Math.sin(t*2)
//     Rj = 1*Math.sin(t*3)+Math.cos(t*2)
//     // for swimmer
//     let Ci = x-Ri, Cj = y-Rj
//     let mag = Math.hypot(Ci,Cj)
//     Ci /= mag/dx
//     Cj /= mag/dx
//     x+= Ci
//     y+= Cj
//     ctx.fillStyle = "blue";
//     ctx.fillRect(canvas.width*r.y + Ri*space, canvas.height*r.x - Rj*space, 1, 1)
//
//     ctx.fillStyle = "red";
//     ctx.fillRect(canvas.width*r.y + x*space, canvas.height*r.x - y*space, 1, 1)
//
//     save(canvas)
//   }
}

// saves the image
function save(canvas){
  const buffer = canvas.toBuffer('image/png')
  fs.writeFileSync('image.png', buffer)
}
function plane(n,m,opt={r:{x:0.5,y:0.5},spacing:15}){
  let {r,spacing} = opt
  tickmarkCount = {x:n.width/spacing,y:n.height/spacing}
  //X-AXIS
  m.beginPath();
  m.font = "8px Arial";
  m.fillStyle = "black";
  m.moveTo(0, n.height*r.x);
  m.lineTo(n.width,n.height*r.x);
  for(let i = 0; i <= tickmarkCount.x; i++){
    // +x
    m.fillRect(spacing*(i)+n.width*r.y,n.height*r.x,1,2); //.fillRect(x,y,breadth,length)
    m.fillText(i,spacing*(i)+n.width*r.y,n.height*r.x+10);
    // -x
    m.fillRect(-spacing*(i)+n.width*r.y,n.height*r.x,1,2);
    m.fillText(-i,-spacing*(i)+n.width*r.y,n.height*r.x+10);
  }
  //Y-AXIS
  m.moveTo(n.width*r.y, 0);
  m.lineTo(n.width*r.y,n.height);
  for(let i = 1; i < tickmarkCount.y; i++) {
    // +y
    m.fillRect(n.width*r.y,spacing*(-i)+n.height*r.x,-2,1);
    m.fillText(i,n.width*r.y+5,spacing*(-i)+n.height*r.x);
    // -y
    m.fillRect(n.width*r.y,spacing*(i)+n.height*r.x,-2,1);
    m.fillText(-i,n.width*r.y+5,spacing*(i)+n.height*r.x);
  }
  m.stroke();
}
