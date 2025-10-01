"""Send CSV-like ventilator data to multiple TCP ports for testing.

Usage examples:
  # send same csv to ports 9001 and 9002, 10 times every 1s
  python multi_simulator.py --ports 9001,9002 --csvs "HR=88,SPO2=96,RR=18,TV=480,FiO2=40" --count 10 --interval 1

  # send different csv per port (semicolon separated list matches ports order)
  python multi_simulator.py --ports 9001,9002 --csvs "HR=88,SPO2=96...;HR=120,SPO2=88..." --count 5

  # use mapping file (each line: port,CSV)
  python multi_simulator.py --mapping-file mapping.csv --count 100 --interval 0.5

"""
import socket
import argparse
import time
from typing import List, Tuple


def send_once(host: str, port: int, msg: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        s.connect((host, port))
        s.sendall(msg.encode('utf-8'))


def parse_ports(s: str) -> List[int]:
    return [int(p.strip()) for p in s.split(',') if p.strip()]


def read_mapping_file(path: str) -> List[Tuple[int, str]]:
    pairs = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # expected format: port,CSV
            if ',' not in line:
                continue
            port_str, csv = line.split(',', 1)
            try:
                port = int(port_str.strip())
            except ValueError:
                continue
            pairs.append((port, csv.strip()))
    return pairs


def main():
    p = argparse.ArgumentParser(description='Multi-ventilator TCP simulator')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--ports', help='Comma separated list of ports, e.g. 9001,9002')
    p.add_argument('--csvs', help='Semicolon-separated CSV strings matching ports order, or a single CSV to use for all ports')
    p.add_argument('--mapping-file', help='Path to file with lines "port,CSV"')
    p.add_argument('--count', type=int, default=1)
    p.add_argument('--interval', type=float, default=1.0, help='Seconds between rounds of sends')
    args = p.parse_args()

    mapping = []  # list of (port, csv)

    if args.mapping_file:
        mapping = read_mapping_file(args.mapping_file)
        if not mapping:
            print('Mapping file provided but no valid entries found.')
            return
    else:
        if not args.ports:
            print('Either --ports or --mapping-file is required')
            return
        ports = parse_ports(args.ports)
        if args.csvs:
            csvs = [c.strip() for c in args.csvs.split(';')]
            if len(csvs) == 1:
                # same csv for all ports
                mapping = [(p, csvs[0]) for p in ports]
            elif len(csvs) == len(ports):
                mapping = list(zip(ports, csvs))
            else:
                print('When using --csvs with multiple ports, provide either a single CSV or the same number of CSVs as ports (semicolon separated).')
                return
        else:
            # no csvs provided, ask user
            print('No CSVs provided. Use --csvs or --mapping-file.')
            return

    print(f"Prepared to send to {len(mapping)} port(s):")
    for port, csv in mapping:
        print(f"  {port} -> {csv}")

    for i in range(args.count):
        for port, csv in mapping:
            try:
                send_once(args.host, port, csv + '\n')
                print(f"[{i+1}/{args.count}] Sent to {args.host}:{port}: {csv}")
            except Exception as e:
                print(f"Send error to {args.host}:{port}: {e}")
        if i < args.count - 1:
            time.sleep(args.interval)


if __name__ == '__main__':
    main()
