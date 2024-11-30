import 'dart:io';

class User{
    final Map<String, dynamic> UserProfile = {
        "name":"",
        "pfp":"",
        "description":"",
        "verified":false,
        "age":false,
        "gender":false
    };
    final Map<String, dynamic> ResearchProfile = {
        "institution":"",
        "qualification":"",
        "verified":false,
        "specialization":"",
        "objective":""
    };

    void setTestData(){
        var testDataUser = ["Venessa Kate", "", "I love to look at the world without a lens.", true, 34, "Female"];
        for(int i = 0; i < testDataUser.length; i++){
            this.UserProfile[this.UserProfile.keys.elementAt(i)]=testDataUser[i];
        }

        var testDataResearcher = ["VIT", "Ph.D", true, "Surgery", "Surgical Methods for PCOS"];
        for(int i = 0; i < testDataResearcher.length; i++){
            this.ResearchProfile[this.ResearchProfile.keys.elementAt(i)]=testDataResearcher[i];
        }
    }

    void fetchData(){

    }

    void getPosts(){

    } 

    void getComments(){

    }

    void displayUser(){
        for(var k in this.UserProfile.keys){
            stdout.write(k + ":");
            print(this.UserProfile[k]);
        }
        for(var k in this.ResearchProfile.keys){
            stdout.write(k + ":");
            print(this.ResearchProfile[k]);
        }
    }

}