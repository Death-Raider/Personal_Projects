from NetworkComponents.relay import Relay

def main():
    relay = Relay(
        'relay1',
        'localhost',
        42069,
        hubs = [
            ('localhost',12345),
            ('localhost',54321)
        ]
    )
    relay.start()

if __name__ == "__main__":
    main()