from gpt4all import GPT4All
model_name = "orca-mini-3b.ggmlv3.q4_0.bin"
model = GPT4All(model_name)


def answer(string):
    global model
    PrePrompting = "Assume you are a farmer assistant chat bod and aim to help other farmers from their doubts, based on this "
    return model.generate(PrePrompting + string, max_tokens=500)

while True:

    print("\n")
    query = str(input())
    if query == 'stop':
        break
    print(answer(query))
