let text_elems = document.getElementsByClassName("td-post-content tagdiv-type")[0]
let all_text = ""
for(let children of text_elems.children){
	all_text += children.textContent
}
console.log(all_text);