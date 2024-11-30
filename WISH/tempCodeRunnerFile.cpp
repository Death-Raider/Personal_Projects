#include<iostream>
#include<string.h>
using namespace std;
int main(){
    int a=256;
    string b = to_string(a);
    cout<<"123"+b<<endl;
    int c=stoi(b);
    cout<<c*2;
    return 0;
}