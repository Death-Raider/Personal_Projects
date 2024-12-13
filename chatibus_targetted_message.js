// run in browser console
const form= document.forms['guest_signup']
const init_form_data = new FormData(form)
init_form_data.set('username', 'Darhgewgfj')
init_form_data.set('sexe', 'homme')
init_form_data.set('age', '19')
init_form_data.set('pays', 'IN')
init_form_data.set('city', 'Tamil Nadu')
await fetch('/user/guest/',{method:'POST', body:init_form_data})
location.replace('/user/guest')
// now open chatib.us/user/guest

const genders = ['femme', 'homme']
const age_range = [18,99]

let people_to_text = 4
let text_per_person = [iiiiiiiiii8
    ["hey", "how are you?"], 
    ["hey","how are you?"], 
    ["hey", "how are you?"],
    ["hey","how are you?"]
]
let gen = 1

// selecting gender
document.getElementsByClassName(`get_users ${genders[gen]}`)[0].click()
await delay(5000)
//get active people
let active_people = [...document.getElementById("chat_online_user").childNodes].filter((e)=> e.tagName=='DIV')
for(let i = 0; i < people_to_text; i++){
    active_people[i].click()
    delay(1000)
    speech_area = document.getElementsByClassName('contentDiv')[0]
    for(let j = 0; j < text_per_person[i].length; j++){
        speech_area.innerText = text_per_person[i][j]
        await delay(1000)
        sendMsg()
        await delay(1000)
    }
    hideMessages()
    await delay(1000)
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// TODO implement class interface to work with individual people tags as objects
// class should have the following methods
/**
 * Class InterfacePeople
 * Method GetActiveCount
 * Method GetPeople
 * Method Update
 * Method FilterByOptions
 * 
 * Class Person
 * Attribute History
 * Method SendMessage
 * Method RecvMessage
 * Method GetDetails
 * Method 
*/