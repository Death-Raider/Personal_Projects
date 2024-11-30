from NetworkComponents.hub import Hub

def main():
    hub1 = Hub('hub1','localhost',12345)
    hub1.start()

if __name__ == "__main__":
    main()