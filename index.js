let ground;
let time = 0;
function setup(){
  let canvas = createCanvas(1510,400);
  ground = new Box(20,20,20,20);
  ground.reset();
  background(51);

}
function mouseDragged(){
  rectMode(CENTER)
  ground.teleport(mouseX,mouseY);
  time = 0;
  ground.reset();
  background(51);

}
function draw(){
  rectMode(CENTER);
  rect(width/2,height,width,20);;
  ground.show();
  if(ground.y + ground.h < height){
    ground.fall(time);
    time+= 0.1;
  }
  else {
    ground.y = height-ground.h;
    time = 0;
  }
}
