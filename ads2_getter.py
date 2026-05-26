import json, os
import dsb_scriptrun

data = {}
ads = dsb_scriptrun.PySim('taupe')
ads.add_input('sine::val')
'''
ads.add_input('') # PSU state
ads.add_input('') # PSU Voltage
ads.add_input('') # PSU Current
ads.add_input('') # SHOP1
ads.add_input('') # SHOP2
ads.add_input('') # PP1
ads.add_input('') # PP1
ads.add_input('') # PP3
ads.add_input('') # PP4
'''
ads.test_start(mode='foreground')
os.makedirs('tmp', exist_ok=True)
data['sine'] = ads.inputs['sine::val'].value
with open('tmp/data.json', 'w') as f:
  json.dump(data, f)