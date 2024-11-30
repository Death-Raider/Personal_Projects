class Box{
  constructor(x,y,w,h){
    this.x = x
    this.y = y
    this.w = w
    this.h = h
  }
  show(){
    rect(this.x,this.y,this.w,this.h)
  }
  move(x,y){
    this.x += x;
    this.y += y;
  }
  teleport(x,y){
    this.x = x;
    this.y = y;
  }
  fall(time){
    this.x += this.velocityX*time
    this.y += this.velocityY*time + 1/2 * this.accelerationY * time * time
    this.velocityY += this.accelerationY*time
  }
  reset(){
    this.velocityX = (winMouseX - pwinMouseX)*0.5;
    this.velocityY = (winMouseY - pwinMouseY)*0.5;
    this.accelerationX = 0;
    this.accelerationY = 5;
  }
}
