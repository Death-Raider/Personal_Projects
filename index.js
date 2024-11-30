const c = document.getElementById("Mycanvas");
const ctx = c.getContext("2d");
const btn = document.getElementById("jump")
const stop = document.getElementById("stop")
const restart = document.getElementById("restart")
const occ = document.getElementById("occ")
const speed = document.getElementById("speed")
const jumpbtn = document.getElementById("jump")
class World{
  constructor(){
    this.gravity = 6;
  }
  floor(){ //creates floor
    ctx.beginPath();
    ctx.fillStyle = "lightgrey";
    ctx.fillRect(0,250,c.width,c.height)
  }
  onFloor(location){//checks collision with floor
    if(location[0][1] + location[1][1] < 250) return +1;
    else if(location[0][1] + location[1][1] == 250) return 0;
    else return -1;
  }
  checkCollision(x,y,x_condition_1=false,x_condition_2=false,y_condition_1=false,y_condition_2=false){// y hitting x
    //calculating x coordinates
    x_condition_1 = ((x.location[0][0]+x.location[1][0])>=y[0][0][0])&&(y[0][0][0]>=x.location[0][0]);
    x_condition_2 = ((x.location[0][0]+x.location[1][0])>=(y[0][0][0]+y[0][1][0]))&&((y[0][0][0]+y[0][1][0])>=x.location[0][0]);
    if(x_condition_1 || x_condition_2){
      //calculating y coordinates
      y_condition_1 = ((x.location[0][1]+x.location[1][1])>=y[0][0][1])&&(y[0][0][1]>=x.location[0][1]);
      y_condition_2 = ((x.location[0][1]+x.location[1][1])>=(y[0][0][1]+y[0][1][1]))&&((y[0][0][1]+y[0][1][1])>=x.location[0][1]);
      if(y_condition_1 || y_condition_2){return true} else {return false}
    }else{return false}
  }
}
class Dyno extends World{
  constructor() {
    super()
    this.jumpStrength = 25;
    this.location = [[60,210],[20,40]]; //[x,y],[width,height]
    this.previousTime = -1;
    this.gravity = 6;
  }
  show(){
    ctx.beginPath();
    ctx.fillStyle = "Black";
    ctx.fillRect(this.location[0][0],this.location[0][1],this.location[1][0],this.location[1][1]);
  }
  remove(){
    ctx.beginPath();
    ctx.fillStyle = "#fff8f8";
    ctx.fillRect(this.location[0][0]-1,this.location[0][1]-1,this.location[1][0]+1,this.location[1][1]+2);//extra added just in case
  }
  jump(t,jump_time){
    this.remove();
    let s2 = (this.jumpStrength*t - this.gravity*t*t/2)//S = ut - (1/2)gt^2
    if(s2 >= 0){
      this.location[0][1] = 210 - s2;
      if(this.onFloor(this.location) == -1) this.location[0][1] = 210;
    }else this.location[0][1] = 210;
    this.previousTime = t;
    t = t+jump_time
    this.show();
    return t
  }
  resetDyno(){
        this.location = [[60,210],[20,40]]; //[x,y],[width,height]
        this.previousTime = -1;
  }
}
class Bullet{
  constructor(){
    this.obj = []
    this.objectSpeed = 5;
    this.occur = 100;
  }
  create(){this.obj.push([[c.width,220],[15,10]])} // addes a bullet
  move(){ // moves all bullets on screen
    for(let i = 0; i < this.obj.length; i++){
      this.remove(this.obj[i]);
      this.obj[i][0][0] -= this.objectSpeed;
      if(this.obj[i][0][0] <= 0) this.obj.splice(i,1)//deletes bullet if it hits the wall
      else this.show(this.obj[i]);
    }
  }
  show(x){
    ctx.beginPath();
    ctx.fillStyle = "Black";
    ctx.fillRect(x[0][0],x[0][1],x[1][0],x[1][1]);
  }
  remove(x){
    ctx.beginPath();
    ctx.fillStyle = "#fff8f8";
    ctx.fillRect(x[0][0]-2,x[0][1],x[1][0]+3,x[1][1]);
  }
  clearBullets(){
      this.obj = []
      this.objectSpeed = 5
      this.occur = 100
  }
}

let world = new World()
let dyno = new Dyno()
let bullet = new Bullet()
let time = 0
let timeJump = 0
let jump_time = 0.1
clear()
world.floor()
dyno.show()

function game(world, dyno, bullet){
    timeJump = dyno.jump(timeJump,jump_time);
    bullet.move();

    if(timeJump == 6) timeJump--;
    jumpbtn.disabled = (world.onFloor(dyno.location) > 0)
    if(bullet.obj.length != 0) if(world.checkCollision(dyno,bullet.obj)) EndInterval();
    if(time%bullet.occur == 50){
        bullet.create();
        let rand_bullet_addition = Math.floor(Math.random()*15)
        if( rand_bullet_addition == 10 ){bullet.create();bullet.create();}
        if( rand_bullet_addition == 5 || rand_bullet_addition == 13 || rand_bullet_addition == 4) bullet.create();
        bullet.objectSpeed += 0.2;
        bullet.occur -= 1
        jump_time += 0.015
    }
    if(bullet.occur <= 50){
        ctx.strokeText("END! U WON!!!",450,150)
        EndInterval()
    };
    occ.innerHTML = "Bullets Left =>"+(bullet.occur-50);
    speed.innerHTML = "Bullet Speed =>"+bullet.objectSpeed.toFixed(2);
    time++
}

let interval

function startInterval(){
    interval = setInterval(game, 20, world, dyno, bullet)
}
function EndInterval(){
    clearInterval(interval)
}

btn.addEventListener('click',()=>{
    timeJump = 0
});
stop.addEventListener('click',()=>{
    EndInterval()
    bullet.clearBullets()
    dyno.resetDyno()
    jump_time = 0.1
    time = 0

});
restart.addEventListener('click',()=>{
    EndInterval()
    bullet.clearBullets()
    dyno.resetDyno()
    jump_time = 0.1
    time = 0
    clear()
    world.floor()
    dyno.show()
    console.log(bullet, dyno)
    startInterval()
});

function clear(){
  ctx.beginPath();
  ctx.fillStyle = "#fff8f8";
  ctx.fillRect(0,0,c.width,c.height);
}
