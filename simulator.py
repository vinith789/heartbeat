"""Simple TCP simulator to send ventilator CSV-like data to a port for testing.
Example:
  python simulator.py --port 9001 --csv "HR=88,SPO2=96,RR=18,TV=480,FiO2=40" --count 5 --interval 1
"""
import socket
import argparse
import time


def send_once(host, port, msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(msg.encode('utf-8'))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, required=True)
    p.add_argument('--csv', required=True, help='CSV-like string to send')
    p.add_argument('--count', type=int, default=1)
    p.add_argument('--interval', type=float, default=1.0)
    args = p.parse_args()

    for i in range(args.count):
        try:
            send_once(args.host, args.port, args.csv + '\n')
            print(f"Sent to {args.host}:{args.port}: {args.csv}")
        except Exception as e:
            print('Send error:', e)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
