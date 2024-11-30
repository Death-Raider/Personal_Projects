document.getElementById('info').click()

function hide(x){
  let content = document.getElementsByClassName("content")
  let btn = document.getElementsByClassName('clicker')

  checking(content,"_hide",x,true)
  checking(btn,"_active",x,false)
}
function checking(cls,adder,x,invert){
  for(let i = 0; i < cls.length; i++){
    if(invert?cls[i].id != cls[x].id:cls[i].id == cls[x].id){
      cls[i].id += adder;
      if(cls[i].id.includes(adder + adder)){
        cls[i].id = cls[i].id.replace(adder,"");
      }
    }else{
      cls[i].id = cls[i].id.replace(adder,"");
    }
  }
}
