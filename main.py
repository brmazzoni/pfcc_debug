import os, sys, subprocess, threading, re, argparse, json
from glob import glob
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.spinner import Spinner
from rich.text import Text


console = Console()

ips = {
  'PFCC1 COM Lane IP': '172.1.254.201',
  'PFCC1 MON Lane IP': '172.1.254.211',
  'PFCC2 COM Lane IP': '172.1.254.202',
  'PFCC2 MON Lane IP': '172.1.254.212',
  'PFCC3 COM Lane IP': '172.1.254.203',
  'PFCC3 MON Lane IP': '172.1.254.213',
  'PFCCTB DPC DEFAULT': '172.28.1.10',
  'PFCCTB DPC 02001': '172.28.1.11',
  'PFCCTB DPC 02004': '172.28.1.14',
  'PFCCTB RTPC DEFAULT': '172.28.1.1',
  'PFCCTB RTPC 02001': '172.28.1.1',
  'PFCCTB RTPC 02004': '172.28.1.4',
}
ips_extended = {
  'PFCC1 COM Lane USER': '172.1.254.101',
  'PFCC1 MON Lane USER': '172.1.254.111',
  'PFCC2 COM Lane USER': '172.1.254.102',
  'PFCC2 MON Lane USER': '172.1.254.112',
  'PFCC3 COM Lane USER': '172.1.254.103',
  'PFCC3 MON Lane USER': '172.1.254.113',
  'PFCC1 COM Lane DEFAULT': '172.1.254.201',
  'PFCC1 MON Lane DEFAULT': '172.1.254.211',
  'PFCC2 COM Lane DEFAULT': '172.1.254.202',
  'PFCC2 MON Lane DEFAULT': '172.1.254.212',
  'PFCC3 COM Lane DEFAULT': '172.1.254.203',
  'PFCC3 MON Lane DEFAULT': '172.1.254.213',
  'TB SUBNET PFCC1 COM Lane USER': '172.28.1.101',
  'TB SUBNET PFCC1 MON Lane USER': '172.28.1.111',
  'TB SUBNET PFCC2 COM Lane USER': '172.28.1.102',
  'TB SUBNET PFCC2 MON Lane USER': '172.28.1.112',
  'TB SUBNET PFCC3 COM Lane USER': '172.28.1.103',
  'TB SUBNET PFCC3 MON Lane USER': '172.28.1.113',
  'TB SUBNET PFCC1 COM Lane DEFAULT': '172.28.1.201',
  'TB SUBNET PFCC1 MON Lane DEFAULT': '172.28.1.211',
  'TB SUBNET PFCC2 COM Lane DEFAULT': '172.28.1.202',
  'TB SUBNET PFCC2 MON Lane DEFAULT': '172.28.1.212',
  'TB SUBNET PFCC3 COM Lane DEFAULT': '172.28.1.203',
  'TB SUBNET PFCC3 MON Lane DEFAULT': '172.28.1.213',
  'COM Lane RESERVE IP': '172.1.254.253',
  'MON Lane RESERVE IP': '172.1.254.254',
  'PFCCTB DPC DEFAULT': '172.28.1.10',
  'PFCCTB DPC 02001': '172.28.1.11',
  'PFCCTB DPC 02004': '172.28.1.14',
  'PFCCTB RTPC DEFAULT': '172.28.1.1',
  'PFCCTB RTPC 02001': '172.28.1.1',
  'PFCCTB RTPC 02004': '172.28.1.4',
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

def ping(args):
  targets = ips_extended if args.extended == True else ips
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
  for name, ip in targets.items():
    t = threading.Thread(target=ping_target, args=(name, ip))
    t.start()
    threads.append(t)

  with Live(console=console, refresh_per_second=10) as live:
    while any(t.is_alive() for t in threads):
      table = Table(show_header=False, box=None, padding=(0, 1))
      table.add_column('Status')
      for name in targets.keys():
        if name in spinners:
          table.add_row(spinners[name])
        else:
          table.add_row(Spinner('dots', text=f'{name}'))
      live.update(table)

    for t in threads:
      t.join()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column('Status')
    for name in targets.keys():
      table.add_row(spinners[name])
    live.update(table)

  n_online = sum(results.values())
  console.print(Text(f'\n   Scan complete: {n_online}/{len(targets)} targets online'), style='red' if n_online == 0 else 'white')

def recon(args):
  ping(args)
  ### ADS2 
  print('\nChecking ADS2 environment...')
  if check_ads2_session(verbose=True):
    data = get_ads2_data()
    print(data)
    print('Checking PSU...')
    print('TODO')
    print('Checking PFCCTB HPP...')
    print('TODO')

  ### TOOLS
  print('\nChecking Tools installation...')
  check_tools()
  
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
  res = subprocess.run(f'binary_udp_loader 172.1.254.201 COM REV', shell=True)
  res = subprocess.run(f'binary_udp_loader 172.1.254.211 MON REV', shell=True)
  return

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


def check_tools():
  if not os.path.exists('C:\\TechSAT\Tools\RELEASE_NOTE'):
    print('   Installed Tools Version: Not Found')
    versions = [None]
  else:
    with open('C:\\TechSAT\Tools\RELEASE_NOTE') as f: notes = f.read()
    found = False
    for line in notes.split('\n'):
      if 'TechSAT Platform Tools Installer RL V' in line:
        match = re.search(r'(V)([0-9\.0-9\.0-9]+)', line)
        if match: 
          found = True
          print('   Installed Tools Version:', match.group(2))
          versions = [match.group(2)]
    if not found:
      print('   Installed Tools Version: Not Found')
      versions = [None]
  res = subprocess.run(['cmd', '/C', 'dir', 'C:\\TechSAT'], capture_output=True, text=True)
  for line in res.stdout.split('\n'):
    if 'Tools' in line:
      match = re.search(r'(Tools_)([0-9\.0-9\.0-9]+)', line)
      if match: versions.append(match.group(2))
  if len(versions) > 1:
    print('\n   Other available Tools Versions:')
    for v in versions[1:]:
      print('    ', v)
  return versions


def swap_tools(version=None):
  versions = check_tools()
  if version is None:
    version = input('\nSwap to version: ')

  if version not in versions:
    print('\nVersion not available.')
    return

  print('\nSwapping to version', version)

  res = subprocess.run(['cmd', '/C', 'move', f'C:\\TechSAT\\Tools', f'C:\\TechSAT\\Tools_{versions[0]}_BKP'])
  print(res)


def translate_bus_silent(log):
  '''
  http://polarion.techsat.net/polarion/#/project/100683_FPCS/wiki/Firmware%20Architecture/IOM%20Binary%20File%20Description%20RL
  '''
  for l in log.split('\n'):
    context = re.findall(r'\[(.*?)\]', l)
    if context == []:
      continue
    useful_bytes = context[-1].split(' ')[:3] # byte1: A429, byte2: CAN, byte3: UART
    bs_string = 'BUS SILENT: '
    for ii, bus_type in enumerate(['A429', 'CAN', 'UART']):
      val = int(useful_bytes[ii], 16)
      bits = format(val, '08b')
      for i, b in enumerate(bits[::-1]):
        if b == '1': bs_string += f'{bus_type}ch{i} '
    res = re.sub(r'\[.*?\]', f'[{bs_string}]', l)
    print(res.strip())


def translate_com_pwr_fail(log):
  for l in log.split('\n'):
    context = re.findall(r'\[(.*?)\]', l)
    if context == []:
      continue
    word = ' '.join(context[-1].split(' ')[:3])
    faults = decode_com_pwr_flt_word(word, verbose=False)
    res = re.sub(r'\[.*?\]', f'[{" ".join(faults)}]', l)
    print(res.strip())


def decode_com_pwr_flt_word(word, verbose=False):
  faults = []
  for i, byte in enumerate(word.split()[:1]): # only first byte is useful
    bits = format(int(byte, 16), '08b') # reads the hex values, converts to bits str
    for pos, b in enumerate(bits[::-1]): #enumerates from right to left
      if i == 0 and pos == 0 and b == '0': faults.append('VCOM_5V_PG FAULT')
      if i == 0 and pos == 1 and b == '0': faults.append('VCOM_5VA_OOR')
      if i == 0 and pos == 2 and b == '0': faults.append('VCOM_15V_OOR')
      if i == 0 and pos == 3 and b == '0': faults.append('FLTn_VCOM_15V FAULT')
  if verbose: print(faults)
  return faults 


def decode_bus_silent_flt_word(word, verbose=False):
  faults = []
  for bus_type, byte in enumerate(zip(['A429', 'CAN', 'UART'], word.split()[:3]): # only first 3 bytes are useful
    bits = format(int(byte, 16), '08b') # reads the hex values, converts to bits str
    for pos, b in enumerate(bits[::-1]): #enumerates from right to left
      print(bus_type, pos, b)
  #if verbose: print(faults)
  #return faults 


def cli():
  parser = argparse.ArgumentParser(description='PFCC debug tool.')
  subparsers = parser.add_subparsers(help='sub-command', dest='subcommand')
  parser_ping = subparsers.add_parser('ping', help='pings PFCC test environment targets')
  parser_ping.add_argument('-e', '--extended', help='use extended ips list', action='store_true', default='False')
  parser_recon = subparsers.add_parser('recon', help='collects information about PFCC test environment')
  parser_recon.add_argument('-e', '--extended', help='use extended ips list', action='store_true', default='False')
  parser_config = subparsers.add_parser('config', help='checks unit\'s configuration')
  parser_tools = subparsers.add_parser('tools', help='checks tools installation')
  parser_decode = subparsers.add_parser('decode', help='decodes fault words')
  parser_decode.add_argument('word', type=str, help='string representation of a 32 bits word in hex')
  parser_decode.add_argument('--com_pwr', help='decode COM PWR fault word')
  parser_decode.add_argument('--bus_silent', help='decode BUS SILENT fault word')

  args = parser.parse_args()
  sc = args.subcommand
  if sc == 'ping':
    ping(args)
  elif sc == 'recon':
    recon(args)
  elif sc in ['config', 'conf']:
    config(args)
  elif sc == 'tools':
    check_tools()
  elif sc == 'decode':
    decode_pwr_flt_word(args.word, verbose=True)
  else:
    parser.print_help()


if __name__ == '__main__':
  com_bus_silent= '''
                Startup: 1572; frame: 496216; time: 34.544637 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496215; time: 34.539401 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496214; time: 34.534534 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496213; time: 34.529392 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496212; time: 34.524722 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496211; time: 34.519474 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496210; time: 34.514509 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496209; time: 34.509403 seconds. Context: [0x12 0x0e 0x4e 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
'''

  mon_bus_silent = '''
Startup: 1208; frame: 496387; time: 2482.591910 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1208; frame: 496386; time: 2482.586911 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1208; frame: 496385; time: 2482.581909 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1208; frame: 496384; time: 2482.576911 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1208; frame: 496383; time: 2482.571913 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1208; frame: 496382; time: 2482.566911 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1208; frame: 496381; time: 2482.561913 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1208; frame: 496380; time: 2482.556910 seconds. Context: [0x00 0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
'''
  com_pwr_fault = '''
                Startup: 1400; frame: 1; time: 1.752734 seconds. Context: [0xd7 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1399; frame: 1; time: 1.752777 seconds. Context: [0xc0 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1397; frame: 1; time: 1.752743 seconds. Context: [0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1396; frame: 1; time: 1.752462 seconds. Context: [0x8d 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1395; frame: 1; time: 1.752780 seconds. Context: [0x37 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1394; frame: 1; time: 1.751878 seconds. Context: [0x20 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1393; frame: 1; time: 1.751617 seconds. Context: [0x53 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1392; frame: 1; time: 1.751575 seconds. Context: [0x7a 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
'''
  translate_com_pwr_fail(com_pwr_fault)