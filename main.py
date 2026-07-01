import os, sys, subprocess, threading, re, argparse, json
from glob import glob
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.spinner import Spinner
from rich.text import Text


console = Console()

com_log = '''Startup counter: 1573.
Error 146: CBIT_ERROR_FPGA_ALL_TRANSFERS_TIMEOUT; total events number: 183350. Last events:
                Startup: 1564; frame: 123072; time: 24.739770 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123071; time: 24.724770 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123070; time: 24.709770 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123069; time: 24.694771 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123068; time: 24.679772 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123067; time: 24.664772 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123066; time: 24.649771 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123065; time: 24.633288 seconds. Context: [0xa8 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()

Error 147: CBIT_ERROR_FPGA_SINGLE_TRANSFER_TIMEOUT; total events number: 733393. Last events:
                Startup: 1564; frame: 123072; time: 24.738773 seconds. Context: [0x8c 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123072; time: 24.737284 seconds. Context: [0x8c 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123072; time: 24.733768 seconds. Context: [0x8c 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123072; time: 24.731745 seconds. Context: [0xa4 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123071; time: 24.723773 seconds. Context: [0x8c 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123071; time: 24.722421 seconds. Context: [0x8c 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123071; time: 24.718904 seconds. Context: [0x8c 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123071; time: 24.717905 seconds. Context: [0xa4 0x9f 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()

Error 151: CBIT_ERROR_FRAME_TIMEOUT_BY_START_SIGNAL; total events number: 183350. Last events:
                Startup: 1564; frame: 123072; time: 24.743582 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123071; time: 24.727246 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123070; time: 24.713407 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123069; time: 24.697147 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123068; time: 24.683462 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123067; time: 24.667180 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123066; time: 24.653410 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1564; frame: 123065; time: 24.635709 seconds. Context: [0x04 0x94 0x10 0x32 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()

Error 152: CBIT_ERROR_FPGA_POWER_MONITOR; total events number: 401. Last events:
                Startup: 1400; frame: 1; time: 1.752734 seconds. Context: [0xd7 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1399; frame: 1; time: 1.752777 seconds. Context: [0xc0 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1397; frame: 1; time: 1.752743 seconds. Context: [0x40 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1396; frame: 1; time: 1.752462 seconds. Context: [0x8d 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1395; frame: 1; time: 1.752780 seconds. Context: [0x37 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1394; frame: 1; time: 1.751878 seconds. Context: [0x20 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1393; frame: 1; time: 1.751617 seconds. Context: [0x53 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1392; frame: 1; time: 1.751575 seconds. Context: [0x7a 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()


Error 153: CBIT_ERROR_FPGA_BUS_SILENT; total events number: 35770953. Last events:
                Startup: 1572; frame: 496216; time: 34.544637 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496215; time: 34.539401 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496214; time: 34.534534 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496213; time: 34.529392 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496212; time: 34.524722 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496211; time: 34.519474 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496210; time: 34.514509 seconds. Context: [0x12 0x0e 0x4f 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
                Startup: 1572; frame: 496209; time: 34.509403 seconds. Context: [0x12 0x0e 0x4e 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00] ()
'''

com_bus_silent= '''Test
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

side = os.getenv('PFCC')
if side is None:
  side = 1

com_ip = f'172.1.254.20{side}'
mon_ip = f'172.1.254.21{side}'

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

def logassert(msg, condition): console.print(msg, Text('OK' if condition else 'KO', style='green' if condition else 'red'))

def ping(args):
  targets = ips
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
    logassert('Checking PSU...', check_power())
    print('Checking PFCCTB HPP... ', end='')
    if data['pp1'] == 0 and data['pp2'] == 0 and data['pp3'] == 0 and data['parity'] == 0: console.print(Text('PFCC1 HPP; ', style='green'), end='')
    if data['shop1'] == 1 and data['shop2'] == 1: console.print('SHOP Mode')


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


def check_power(verbose=False):
  data = get_ads2_data()
  c1 = data['psu1_state'] == 1
  c2 = data['psu2_state'] == 1
  c3 = 27 < data['psu1_voltage'] < 29
  c4 = 27 < data['psu2_voltage'] < 29
  c5 = 0.4 < data['psu1_current'] < 0.5
  c6 = 0.4 < data['psu2_current'] < 0.5
  return (c1 or c2) and (c3 or c4) and (c5 or c6)

def check_shop_mode(verbose=False):
  data = get_ads2_data()
  c7 = data['shop1'] == 1
  c8 = data['shop2'] == 1
  return c7 and c8


def config(raw=True):
  if raw:
    print('\nCOM CONFIG:')
    res = subprocess.run(f'binary_udp_loader {com_ip} COM REV', shell=True)
    print('\nMON CONFIG:')
    res = subprocess.run(f'binary_udp_loader {mon_ip} MON REV', shell=True)
    return
  else:
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


def decode_com_pwr_flt_word(word, verbose=False):
  '''
  http://polarion.techsat.net/polarion/#/project/100683_FPCS/wiki/Firmware%20Architecture/IOM%20Binary%20File%20Description%20RL
  '''
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
  for bus_type, byte in zip(['UART', 'CAN', 'A429'], word.split()[1:]):
    bits = format(int(byte, 16), '08b') # reads the hex values, converts to bits str
    for pos, b in enumerate(bits[::-1]): # enumerates from right to left
      if b == '1': faults.append(f'{bus_type} CH{pos} SILENT')
  if verbose: print(faults)
  return faults 


def translate_fault_log(log, decode_func, verbose=False):
  log_dict = {}
  for l in log.split('\n'):
    context = re.findall(r'\[(.*?)\]', l)
    if not context:
      if verbose: print(l)
      continue
    word = ' '.join(context[-1].split(' ')[:3])
    faults = decode_func(word, verbose=False)
    res = re.sub(r'\[.*?\]', f'[{"; ".join(faults)}]', l)
    log_entry = {}
    log_entry['startup'] = int(re.findall(r'Startup: (.*?);', l)[0])
    log_entry['frame'] = int(re.findall(r'frame: (.*?);', l)[0])
    log_entry['time'] = float(re.findall(r'time: (.*?) seconds', l)[0])
    log_dict[log_entry['startup']*log_entry['frame']] = log_entry
  log_dict = sorted(log_dict.items())
  if verbose:
    for metaframe, entry in log_dict:
      console.print('startup:', entry['startup'], 'frame:', entry['frame'], 'faults:', Text('; '.join(faults), style='red'))
  return log_dict


def extract_flt_blocks(log):
  blocks = {}
  res = re.findall(r'Error (.*?)(?:\n\n|$)', log, re.DOTALL)
  for r in res:
    err = re.findall(r'[0-9]+: (.*?);', r)[0]
    logs = '\n'.join(r.split('\n')[1:])
    blocks[err] = logs
  return blocks


def reg2log():
  com_log = []
  console.print('Checking ADS2 session... ', end='')
  if check_ads2_session(): console.print(Text('OK', style='green'))
  else:
    console.print(Text('KO', style='red'))
    return
  
  console.print('Checking SHOP mode... ', end='')
  if check_shop_mode() and check_power(): console.print(Text('OK', style='green'))
  else:
    console.print(Text('KO', style='red'))
    return
  # run COM, save raw file and grab blocks
  res = subprocess.run(['platform_error_handle', '-ip', com_ip, '-trg', 'PFCC_COM'], text=True, capture_output=True)
  print(res.stdout)
  blocks = extract_flt_blocks(res.stdout)
  for err, logs in blocks.items():
    print(err)
    print(logs)
    #log.append
  # do same for MON

def cli():
  parser = argparse.ArgumentParser(description='PFCC debug tool.')
  subparsers = parser.add_subparsers(help='sub-command', dest='subcommand')

  ### MISC ###
  parser_ping = subparsers.add_parser('ping', help='pings PFCC test environment targets')
  parser_ping.add_argument('-e', '--extended', help='use extended ips list', action='store_true', default='False')
  parser_recon = subparsers.add_parser('recon', help='collects information about PFCC test environment')
  parser_recon.add_argument('-e', '--extended', help='use extended ips list', action='store_true', default='False')
  parser_config = subparsers.add_parser('config', help='checks unit\'s configuration')
  parser_tools = subparsers.add_parser('tools', help='checks tools installation')
  
  ### DECODE ###
  parser_decode = subparsers.add_parser('decode', help='decodes fault words')
  parser_decode.add_argument('word', type=str, help='string representation of a 32 bits word in hex')
  decode_group = parser_decode.add_mutually_exclusive_group(required=True)
  decode_group.add_argument('--com_pwr', help='decode COM PWR fault word', action='store_true')
  decode_group.add_argument('--bus_silent', help='decode BUS SILENT fault word', action='store_true')

  parser_translate = subparsers.add_parser('translate', help='translate fault log')
  parser_translate.add_argument('log', type=str, help='string representation of a 32 bits word in hex')
  translate_group = parser_translate.add_mutually_exclusive_group(required=True)
  translate_group.add_argument('--com_pwr', help='decode COM PWR fault word', action='store_true')
  translate_group.add_argument('--bus_silent', help='decode BUS SILENT fault word', action='store_true')

  parser_reg2log = subparsers.add_parser('reg2log', help='reads registers from PFCC and creates a log file')

  args = parser.parse_args()
  sc = args.subcommand
  if sc == 'ping': ping(args)
  elif sc == 'recon': recon(args)
  elif sc == 'config': config()
  elif sc == 'tools': check_tools()
  elif sc == 'decode':
    if args.bus_silent == True: decode_bus_silent_flt_word(args.word, verbose=True)
    elif args.com_pwr == True: decode_com_pwr_flt_word(args.word, verbose=True)
    else: raise Exception('WTF?')
  elif sc == 'translate':
    if args.bus_silent == True: translate_fault_log(com_bus_silent, decode_bus_silent_flt_word)
    elif args.com_pwr == True: translate_fault_log(com_pwr_fault, decode_com_pwr_flt_word)
    else: raise Exception('WTF?')
  elif sc == 'reg2log': reg2log()
  else: parser.print_help()


if __name__ == '__main__':
  #print('Run debug subcommand')
  print() 
  extract_flt_blocks(sys.stdin.read())