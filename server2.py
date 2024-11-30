from NetworkComponents.hub import Hub

def main():
    hub1 = Hub('hub2','localhost',54321)
    hub1.start()

if __name__ == "__main__":
    main()