var c = document.getElementById("myCanvas");
var ctx = c.getContext("2d");

myCanvas.addEventListener('mousedown', startPainting);
myCanvas.addEventListener('mouseup', stopPainting);
myCanvas.addEventListener('mousemove', sketch);

var bufferSpace = 3;//in px
bufferSpace = bufferSpace/50;//converts buffer space into the fractional value

lineCountX = (c.height/50)-1;
lineCountY = (c.width/50)-1;

var boxGridX = [];
var boxGridY = [];
//creates the grid
makeGrid()
function makeGrid(){
  ctx.fillStyle = "darkgrey";
  ctx.fillRect(0, 0, c.width, c.height);

  ctx.beginPath();
  for(let a = 1; a < (c.width/50); a++){
    //creates the lines vertical lines
    ctx.moveTo((c.width/8)*a,0);
    ctx.lineTo((c.width/8)*a,c.height);
    //recreates the lines casue they are not fully black before
    ctx.moveTo((c.width/8)*a,c.height);
    ctx.lineTo((c.width/8)*a,0);
    //makes em black
    ctx.strokeStyle = "black";
  }
  for(let b = 1; b < (c.height/50); b++){
    //creates the lines horizontal lines
    ctx.moveTo(0,(c.height/12)*b);
    ctx.lineTo(c.width,(c.height/12)*b);
    //recreates the lines casue they are not fully black before
    ctx.moveTo(c.width,(c.height/12)*b);
    ctx.lineTo(0,(c.height/12)*b);
    //makes em black
    ctx.strokeStyle = "black";
  }
  ctx.stroke();
}

// Stores the initial position of the cursor
let coord = {x:0 , y:0};
let paint = false;
function getPosition(event){
  coord.x = event.clientX - c.offsetLeft;
  coord.y = event.clientY - c.offsetTop;
  coord.xGrid = coord.x/50;
  coord.yGrid = coord.y/50;
}
function startPainting(event){
  paint = true;
  getPosition(event);
}
function stopPainting(){
  paint = false;
}
function sketch(event){
  if (!paint) return;
  getPosition(event);
  if(coord.xGrid-Math.floor(coord.xGrid) > bufferSpace && coord.yGrid-Math.floor(coord.yGrid) > bufferSpace){
    ctx.fillStyle = "white";
    ctx.fillRect(Math.floor(coord.xGrid)*50,Math.floor(coord.yGrid)*50,50,50);
    boxGridX.push(Math.floor(coord.xGrid));
    boxGridY.push(Math.floor(coord.yGrid));
  }
}
function clearScreen(){
  makeGrid()
  boxGridX.length = 0;
  boxGridY.length = 0;
  console.log(boxGridX,boxGridY);
}