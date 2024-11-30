getData();
async function getData(){
  const responce =  await fetch('/datastore');
  const data = await responce.json();
  document.getElementById("load").style.display = 'none';
  for(item of data){
    const center = document.createElement('center')
    const root = document.createElement('div');
    const problem = document.createElement('div');
    const geo = document.createElement('div');
    const date = document.createElement('div');

    problem.textContent = `problem: ${item.problem}`
    geo.textContent = `geo: ${item.lat}, ${item.long}`;
    const dateString = new Date(item.timestamp);
    date.textContent = dateString;

    root.append(problem,geo,date);
    center.append(root)
    document.body.append(center);
  }
}
