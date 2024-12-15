let box;
let time = 0;
function setup(){
  let canvas = createCanvas(1510,400);
  box = new Box(20,20,20,20);
  box.reset();
  background(51);

}
function mouseDragged(){
  rectMode(CENTER)
  box.teleport(mouseX,mouseY);
  time = 0;
  box.reset();
  background(51);

}
function draw(){
  rectMode(CENTER);
  rect(width/2,height,width,20);;
  box.show();
  if(box.y + box.h < height){
    box.fall(time);
    time+= 0.1;
  }
  else {
    box.y = height-box.h;
    time = 0;
  }
}
