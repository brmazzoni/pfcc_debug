import json, os
import dsb_scriptrun

data = {}
ads = dsb_scriptrun.PySim('ads2_getter')
#ads.add_input('sine::val')

# Sorensen PSUs
ads.add_input('PSU-1::deviceState')
ads.add_input('PSU-2::deviceState')
ads.add_input('PSU-1::rbVoltage')
ads.add_input('PSU-2::rbVoltage')
ads.add_input('PSU-1::rbCurrent')
ads.add_input('PSU-2::rbCurrent')

# ITECH PSUs
ads.add_input('FIB_TechSAT_PSU_DC_IT6000C_A::Device_State')
ads.add_input('FIB_TechSAT_PSU_DC_IT6000C_B::Device_State')
ads.add_input('FIB_TechSAT_PSU_DC_IT6000C_A::Voltage_Measure')
ads.add_input('FIB_TechSAT_PSU_DC_IT6000C_B::Voltage_Measure')
ads.add_input('FIB_TechSAT_PSU_DC_IT6000C_A::Current_Measure')
ads.add_input('FIB_TechSAT_PSU_DC_IT6000C_B::Current_Measure')

ads.add_input('DSIO::ADS2.PFCC.DIS_SHOP_1.state')
ads.add_input('DSIO::ADS2.PFCC.DIS_SHOP_2.state')
ads.add_input('DSIO::ADS2.PFCC.PP1.state')
ads.add_input('DSIO::ADS2.PFCC.PP2.state')
ads.add_input('DSIO::ADS2.PFCC.PP3.state')
ads.add_input('DSIO::ADS2.PFCC.Parity.state')

ads.test_start(mode='foreground')
os.makedirs('tmp', exist_ok=True)
#data['sine'] = ads.inputs['sine::val'].value
data['psu1_state'] = max(ads.inputs['PSU-1::deviceState'].value, ads.inputs['FIB_TechSAT_PSU_DC_IT6000C_A::Device_State'].value)
data['psu2_state'] = max(ads.inputs['PSU-2::deviceState'].value, ads.inputs['FIB_TechSAT_PSU_DC_IT6000C_B::Device_State'].value)
data['psu1_voltage'] = max(ads.inputs['PSU-1::rbVoltage'].value, ads.inputs['FIB_TechSAT_PSU_DC_IT6000C_A::Voltage_Measure'].value)
data['psu2_voltage'] = max(ads.inputs['PSU-2::rbVoltage'].value, ads.inputs['FIB_TechSAT_PSU_DC_IT6000C_B::Voltage_Measure'].value)
data['psu1_current'] = max(ads.inputs['PSU-1::rbCurrent'].value, ads.inputs['FIB_TechSAT_PSU_DC_IT6000C_A::Current_Measure'].value)
data['psu2_current'] = max(ads.inputs['PSU-2::rbCurrent'].value, ads.inputs['FIB_TechSAT_PSU_DC_IT6000C_B::Current_Measure'].value)
data['shop1'] = ads.inputs['DSIO::ADS2.PFCC.DIS_SHOP_1.state'].value
data['shop2'] = ads.inputs['DSIO::ADS2.PFCC.DIS_SHOP_2.state'].value
data['pp1'] = ads.inputs['DSIO::ADS2.PFCC.PP1.state'].value
data['pp2'] = ads.inputs['DSIO::ADS2.PFCC.PP2.state'].value
data['pp3'] = ads.inputs['DSIO::ADS2.PFCC.PP3.state'].value
data['parity'] = ads.inputs['DSIO::ADS2.PFCC.Parity.state'].value

with open('tmp/data.json', 'w') as f:
  json.dump(data, f)