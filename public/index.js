const mymap = L.map('mmap').setView([0, 0], 1);//setVied([lat,long],zoom)
const data = {};

start()
async function start(){
  const call = await fetch('/datastore');
  const locations = await call.json();

  var markers = new Array(locations.length);
  console.log("locations",locations);
  for(let i = 0; i < markers.length; i++){
    markers[i] = L.marker([0,0]).addTo(mymap);
    markers[i].setLatLng([locations[i].lat,locations[i].long]);
  }
  var myMarker = L.marker([0,0]).addTo(mymap);

  const attribution =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
  const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  L.tileLayer(tileUrl, {attribution}).addTo(mymap);

  document.getElementById('ToC').style.display ='block';
  document.getElementById('ToC').style.width ='150px';

  if ("geolocation" in navigator){
    navigator.geolocation.getCurrentPosition( async position => {

      const lat = position.coords.latitude;
      const long = position.coords.longitude;

      myMarker.setLatLng([lat,long])
      mymap.setView([lat,long],8)

      document.getElementById('load').style.display = "none";
      document.getElementById('latit').style.display = "block";
      document.getElementById('longi').style.display = "block";

      document.getElementById('latitude').textContent = lat;
      document.getElementById('longitude').textContent = long;

      data.lat = lat;
      data.long = long;
    });
  }
  else{
    alert("unaviliable geolocation");
  }
}

function sendDataLOL(){
  data.problem = document.getElementById('problem').value;
  alert("Sending problem");
  responceServer();
}
//sends data and logs the responce
async function responceServer(){
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };
  const responce = await fetch('/prob',options);
  const jsonget = await responce.json();
  alert('Problem is sent');
  alert(jsonget);
}
//gets the data to display on map
function ToC(){
  alert('Are you sure?');
  document.getElementById('btn').style.display = 'block';
  document.getElementById('ToC').style.display = 'none';
  document.getElementById('conditions').style.display = 'none';
}
