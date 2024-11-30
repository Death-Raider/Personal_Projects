import autopy as auto
import sys, json

#Read data from stdin
def read_in():
    value = sys.stdin.readlines()[0]
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(value)
def predict():
    stonks = read_in()
    if stonks == 'UP':
        #alertMe('UP')
        auto.mouse.move(1440, 370)
        auto.mouse.click()
    elif stonks == 'DOWN':
        #alertMe('DOWN')
        auto.mouse.move(1440, 440)
        auto.mouse.click()
    else :
        #alertMe('SAME')
        auto.mouse.move(1440, 440)
        auto.mouse.click()
def main():
    #get our data as an array from read_in()
    predict()
#start process
if __name__ == '__main__':
    main()
