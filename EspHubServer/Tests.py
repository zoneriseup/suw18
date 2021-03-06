import json
from sqlalchemy import desc
from DataAccess import DBA, DAC, DAO
import time
from Config.Config import Config
from datetime import datetime, timedelta
from main import data_parsing

if __name__ == '__main__':
	conf = Config.get_config()
	# section = conf.items('mqtt')
	# print(section)

	with DAC.keep_session() as db:
		now = datetime.now()
		past = now - timedelta(1)
		records = data_parsing.get_records_for_charts('6621b8a0-b0ff-49f8-ac6f-06efaf4b131a', 'weather_karvina', past, now, summarization='hourly')
		print(json.dumps(records))
#
# with DAC.keep_session() as db:
# 	devices = db.query(DAO.Device, DAO.Ability).join(DAO.Device.abilities).filter(DAO.Ability.category == DAO.Ability.CATEGORY_DISPLAY).all()
# 	response = []
# 	for device, ability in devices:
# 		# print(device.serialize(), ability.serialize())
# 		response.append({'id': device.id, 'name': device.name, 'ability_name': ability.name, 'ability_user_name': ability.user_name, 'ability_description': ability.description})
#
# 	print(response)

# with DAC.keep_session() as db:
# 	db.add(DAO.Record(name='switch', value='on', device_id='828530', time=datetime.now()))

# with DAC.keep_session() as db:
# 	# record = db.query(DAO.Record).get(375)
# 	device = DBA.get_device(db, '383646ee-fe07-4660-940e-51f5b33a6cf6')
# 	print(device)
#
# 	records = DBA.get_record_from_device(db, '828530', 'switch', limit=5)
# 	for record in records:
# 		print(record.id, record.time)

# with DAC.keep_session() as dbs:
# 	dev = DAO.Device(id='dev1234', name='My Test device', provided_func=['temp', 'hum'], status=DAO.Device.VALIDATED)
# 	# dbs.add(dev)
#
# 	# DBA.add_waiting_device(dbs, dev)
# 	DBA.insert_device(dbs, dev)
# 	dbs.add(DAO.Ability(name='temp', io='in', category='sensor', unit='C', device=dev))
#
# 	for i in range(26, 32):
# 		DBA.insert_record(dbs, DAO.Record(name='temp', value=str(i), device=dev, time=datetime.now()))
# 		time.sleep(0.1)

# for i in range(300, 310):
# 	DBA.insert_record(dbs, DAO.Record(name='light', value=str(i), device=dev, time=datetime.now()))
# 	time.sleep(0.1)

# ability = DAO.Ability(device=dev)
# print(ability)
# json_str = {'name': 'ability1', 'user_name': 'Ability One', 'io': 'output'}
# ability.init_with_json(json.dumps(json_str))
# print(ability)
# dbs.add(ability)
# print(ability.to_json())

# with DAC.keep_session() as dbs:
# dev = dbs.query(DAO.Device).filter(DAO.Device.id == 'dev1234').first()
# dev = DBA.get_device(dbs, 'dev1234')
# print(dev)
# DBA.remove_device(dbs, 'dev1234', cascade=False)
# dev.provided_func = ['temp', 'hum', 'light']
# records = DBA.get_record_from_device(dbs, 'dev1234', value_type='temp', order='upscend', limit=5)
# for record in records:
# 	print(record)

# print('--------------')
# with DAC.keep_session() as dbs:
# 	print(dbs.query(DAO.Device).all())
# 	print(DBA.get_devices(dbs))

# from main import data_parsing
# print(data_parsing.get_actual_device_values('dev1234'))
# print(data_parsing.get_records_for_charts('dev1234', 'temp', '', ''))
# print(data_parsing.get_all_input_abilities())

# from DataAccess import DBA
# with DAC.keep_session() as dbs:
# 	print(DBA.get_devices(dbs))
# from Config.Config import Config
# conf = Config.get_config()
# print(conf.getint('discovery', 'interval'))
