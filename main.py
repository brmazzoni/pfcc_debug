import os, sys, subprocess, threading, re, argparse, json
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.spinner import Spinner
from rich.text import Text


console = Console()

targets_ips = {
  'PFCC1 COM Lane': '172.1.254.101',
  'PFCC1 MON Lane': '172.1.254.111',
  'PFCC2 COM Lane': '172.1.254.102',
  'PFCC2 MON Lane': '172.1.254.112',
  'PFCC3 COM Lane': '172.1.254.103',
  'PFCC3 MON Lane': '172.1.254.113',
  'PFCC1 COM Lane DEFAULT IP': '172.1.254.201',
  'PFCC1 MON Lane DEFAULT IP': '172.1.254.211',
  'PFCC2 COM Lane DEFAULT IP': '172.1.254.202',
  'PFCC2 MON Lane DEFAULT IP': '172.1.254.212',
  'PFCC3 COM Lane DEFAULT IP': '172.1.254.203',
  'PFCC3 MON Lane DEFAULT IP': '172.1.254.213',
  'TB SUBNET PFCC1 COM Lane': '172.28.1.101',
  'TB SUBNET PFCC1 MON Lane': '172.28.1.111',
  'TB SUBNET PFCC2 COM Lane': '172.28.1.102',
  'TB SUBNET PFCC2 MON Lane': '172.28.1.112',
  'TB SUBNET PFCC3 COM Lane': '172.28.1.103',
  'TB SUBNET PFCC3 MON Lane': '172.28.1.113',
  'TB SUBNET PFCC1 COM Lane DEFAULT IP ': '172.28.1.201',
  'TB SUBNET PFCC1 MON Lane DEFAULT IP': '172.28.1.211',
  'TB SUBNET PFCC2 COM Lane DEFAULT IP': '172.28.1.202',
  'TB SUBNET PFCC2 MON Lane DEFAULT IP': '172.28.1.212',
  'TB SUBNET PFCC3 COM Lane DEFAULT IP': '172.28.1.203',
  'TB SUBNET PFCC3 MON Lane DEFAULT IP': '172.28.1.213',
  'COM Lane RESERVE IP': '172.1.254.253',
  'MON Lane RESERVE IP': '172.1.254.254',
  'PFCCTB DPC': '172.28.1.10',
  'PFCCTB RTPC': '172.28.1.1',
}

targets = {
  'PFCC1 COM Lane': {
    'type': 'COM',
    'ip': '172.1.254.101',
  },
  'PFCC1 MON Lane': {
    'type': 'MON',
    'ip': '172.1.254.111',
  },
  'PFCC2 COM Lane': {
    'type': 'COM',
    'ip': '172.1.254.102',
  },
  'PFCC2 MON Lane': {
    'type': 'MON',
    'ip': '172.1.254.112',
  },
  'PFCC3 COM Lane': {
    'type': 'COM',
    'ip': '172.1.254.103',
  },
  'PFCC3 MON Lane': {
    'type': 'MON',
    'ip': '172.1.254.113',
  },
}

# QTP configuration
expected = {
  'COM': {
    'PLSW_PFCC_RL_BTLDR': '0xCB79D41D',
    'PLSW_PFCC_RL_COM_DATALOADER': '0x6DE0377B',
    'PLSW_PFCC_RL_COM_CORE': '0x7FB0F7BF',
    'PLSW_PFCC_RL_COM_CORE_DEBUG': '0x5F750AA7',
    'Firmware': '0x01010002'
  },
  'MON': {
    'PSW_PFCC_MON_RL_BTLDR': '',
  },
}


def recon():
  results = {}
  spinners = {}
  lock = threading.Lock()

  def ping_target(name, ip):
    with lock: spinners[name] = Spinner('dots', text=f'{name} - {ip}')
    res = subprocess.run(['ping', '-n', '1', '-w', '3000', ip], capture_output=True, text=True)
    with lock:
      if res.returncode == 0 and 'Reply from' in res.stdout:
        results[name] = True
        spinners[name] = Text(f'✓ {name} - {ip}', style='green')
      else:
        results[name] = False
        spinners[name] = Text(f'  {name} - {ip}')

  print('\nEnumerating connected UUT and TB...\n')
  threads = []
  for name, ip in targets_ips.items():
    t = threading.Thread(target=ping_target, args=(name, ip))
    t.start()
    threads.append(t)

  with Live(console=console, refresh_per_second=10) as live:
    while any(t.is_alive() for t in threads):
      table = Table(show_header=False, box=None, padding=(0, 1))
      table.add_column('Status')
      for name in targets_ips.keys():
        if name in spinners:
          table.add_row(spinners[name])
        else:
          table.add_row(Spinner('dots', text=f'{name}'))
      live.update(table)

    for t in threads:
      t.join()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column('Status')
    for name in targets_ips.keys():
      table.add_row(spinners[name])
    live.update(table)

  print(f'\nScan complete: {sum(results.values())}/{len(targets_ips)} targets online')

  ### ADS2 
  print('\nChecking ADS2 environment...')
  if check_ads2_session(verbose=True):
    data = get_ads2_data()
    print(data)
    print('Checking PSU...')
    print('TODO')
    print('Checking PFCCTB HPP...')
    print('TODO')
  
def check_ads2_session(verbose=False):
  res = subprocess.run(['ads2', 'session', 'state'], capture_output=True, text=True)
  if res.returncode != 0:
    if verbose: console.print(Text('   Not connected to TB'))
    return False
  elif 'clusterstate = "RUN_LOADED";' not in res.stdout:
    if verbose: console.print(Text('   ADS2 session is NOT running', style='red'))
    return False

  elif 'clusterstate = "RUN_LOADED";' in res.stdout:
    if verbose: console.print(Text(' ✓ ADS2 session is running', style='green'))
    return True
  else:
    raise Exception(f'Unhandled ADS2 session state:\n{res}')


def config(args):
  target = args.target
  res = subprocess.run(['binary_udp_loader', targets[target]['ip'], targets[target]['type'], 'REV'], capture_output=True, text=True)
  print(res.stdout)

  all_match = True

  for key, expected_crc in expected[targets[target]['type']].items():
    found = False
    for line in res.stdout.split('\n'):
      if key in line:
        # Look for hex pattern (0x followed by hex digits)
        match = re.search(r'(0x[0-9A-Fa-f]+)', line)
        if match:
          actual_crc = match.group(1)
          if actual_crc.upper() == expected_crc.upper():
            print(f'  ✓ {key}: {actual_crc} (match)')
          else:
            print(f'  ✗ {key}: {actual_crc} (expected: {expected_crc})')
            all_match = False
          found = True
          break
    if not found:
      print(f'  ✗ {key}: not found in output (expected: {expected_crc})')
      all_match = False

  if all_match:
    print('\nAll CRC values match!')
  else:
    print('\nSome CRC values do not match!')


def get_ads2_data():
  subprocess.run(['ads2', 'python', 'ads2_getter.py'])
  with open('tmp/data.json') as f:
    data = json.load(f)
  return data


def test():
  pass


def cli():
  parser = argparse.ArgumentParser(description='PFCC debug tool.')
  subparsers = parser.add_subparsers(help='sub-command', dest='subcommand')
  
  parser_recon = subparsers.add_parser('recon', help='pings pfcc targets')
  parser_config = subparsers.add_parser('config', help='checks unit\'s configuration')
  parser_config.add_argument('-t', '--target', help='target name (COM FPGA, MON MCU, ...)')
  parser_test = subparsers.add_parser('test', help='test function')

  args = parser.parse_args()
  sc = args.subcommand
  if sc == 'recon':
    recon()
  elif sc in ['config', 'conf']:
    config(args)
  elif args.subcommand == 'test':
    test()
  else:
    parser.print_help()
  

if __name__ == '__main__':
  test()
