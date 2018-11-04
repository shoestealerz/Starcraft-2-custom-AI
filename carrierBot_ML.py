import sc2

from sc2 import run_game, maps, Race, Difficulty, position, Result

from sc2 import run_game, maps, Race, Difficulty, position

from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
CYBERNETICSCORE, STALKER, ZEALOT, STARGATE, VOIDRAY, CARRIER, FLEETBEACON,\
ROBOTICSFACILITY, OBSERVER
import random
import cv2
import numpy as np

import time
import keras
import os




HEADLESS = False
class MyProtossBot(sc2.BotAI):


	def __init__(self, use_model = False):
		self.ITERATIONS_PER_MIN = 165
		self.MAX_WORKERS= 65
		self.wait_duration=0
		self.use_model = use_model

		self.train_data =[]
		if self.use_model:
			print("USING MODEL!")
			self.model = keras.models.load.model(BasicCNN-10-epochs-0.0001-LR-STAGE1)

	def on_end(self, game_result):
		print ('--- on_end called ---')
		print(game_result, self.use_model)

		if game_result == Result.Victory:
			np.save("train_data/{}.npy".format(str(int(time.time()))), np.array(self.train_data))

		with open("log.txt", "a") as f:
			if self.use_model:
				f.write("Model {}\n".format(game_result))
			else:
				f.write("Random {}\n".format(game_result))

	def __init__(self):
		self.ITERATIONS_PER_MIN = 165
		self.MAX_WORKERS= 65
		self.wait_duration=0
		self.train_data = []



	async def on_step(self, iteration):
		self.iteration = iteration
		await self.distribute_workers();
		await self.build_workers();
		await self.build_pylons();
		await self.build_gas();
		await self.smart_expand();
		await self.army_buildings();
		await self.army_units();
		await self.attack();
		await self.intel();
		await self.scout();

	async def intel(self):
		#UNIT: [SIZE, COLOR]
		draw_dict = {

					 NEXUS: [15, (0, 255, 0)],
					 PYLON: [3, (20, 235, 0)],
					 PROBE: [1, (55, 200, 0)],
					 ASSIMILATOR: [2, (55, 200, 0)],
					 GATEWAY: [3, (200, 100, 0)],
					 CYBERNETICSCORE: [3, (150, 150, 0)],
					 STARGATE: [5, (255, 0, 0)],
					 VOIDRAY: [3, (255, 100, 0)],
					 CARRIER: [3, (255,120, 0)],
					 ROBOTICSFACILITY: [5, (215, 155, 0)],
					 #OBSERVER: [3, (255, 255, 255)]
					}
		# for game_info: https://github.com/Dentosal/python-sc2/blob/master/sc2/game_info.py#L162
		#print(self.game_info.map_size)


		# for game_info: https://github.com/Dentosal/python-sc2/blob/master/sc2/game_info.py#L162
		print(self.game_info.map_size)

		# flip around. It's y, x when you're dealing with an array.
		game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)



		for unit_type in draw_dict:
			for unit in self.units(unit_type).ready:
				pos = unit.position
				cv2.circle(game_data, (int(pos[0]), int(pos[1])), draw_dict[unit_type][0], draw_dict[unit_type][1], -1)  # BGR

		#drawing enemy buildings, only main bases are different
		main_base_names =["nexus", "commandcenter","hatchery"]	
		for enemy_building in self.known_enemy_structures:
			pos = enemy_building.position
			if enemy_building.name.lower() not in main_base_names:
				cv2.circle(game_data, (int(pos[0]), int(pos[1])), 5, (200, 50, 212), -1)
		for enemy_building in self.known_enemy_structures:
			pos = enemy_building.position
			if enemy_building.name.lower() in main_base_names:
				cv2.circle(game_data, (int(pos[0]), int(pos[1])), 15, (0, 0, 255), -1)
		#drawing enemy units, only workers are different
		for enemy_unit in self.known_enemy_units:

			if not enemy_unit.is_structure:
				worker_names =["probe", "drone", "scv"]

				pos = enemy_unit.position
				if enemy_unit.name.lower() in worker_names:
					cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
				else:
					cv2.circle(game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)

		#drawing the unit OBSERVER
		for obs in self.units(OBSERVER).ready:
			pos = obs.position
			cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (255, 255, 255), -1)



		#visualizations for resources, supply and army
		line_max=50

		mineral_ratio = self.minerals/1500
		if mineral_ratio >1.0:
			minteral_ratio =1.0

		gas_ratio = self.vespene/1500
		if gas_ratio >1.0:
			gas_ratio =1.0

		if not self.supply_cap ==0:
			supply_ratio = self.supply_left / self.supply_cap
		if supply_ratio>1.0:
			supply_ratio=1.0

		plausible_supply = self.supply_cap/ 200.0

		military_weight = (self.units(CARRIER).amount * 6)/(self.supply_cap - self.supply_left)
		if military_weight >1.0:
			military_weight =1.0

		#
		cv2.line(game_data, (0, 19), (int(line_max*military_weight), 19), (250, 250, 200), 3)
		cv2.line(game_data, (0, 15), (int(line_max*plausible_supply), 15), (220, 200, 200), 3)
		cv2.line(game_data, (0, 11), (int(line_max*mineral_ratio), 11), (150, 150, 150), 3)
		cv2.line(game_data, (0, 7), (int(line_max*gas_ratio), 7), (210, 200, 0), 3)
		cv2.line(game_data, (0, 3), (int(line_max*supply_ratio), 3), (0, 255, 25), 3)



		#flip horizontally to make our final fix in visual representation:
		self.flipped = cv2.flip(game_data, 0)

		if not HEADLESS:
			resized = cv2.resize(self.flipped, dsize=None, fx=2, fy=2)

			cv2.imshow('Intel', resized)
			cv2.waitKey(1)

		resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)

		cv2.imshow('Intel', resized)
		cv2.waitKey(1)


	async def build_workers(self):
		if self.units(NEXUS).amount *22 >self.units(PROBE).amount:
			if self.units(PROBE).amount < self.MAX_WORKERS:
				for nexus in self.units(NEXUS).ready.noqueue:
					if self.can_afford(PROBE):
						await self.do(nexus.train(PROBE));


	async def build_pylons(self):
		if self.units(FLEETBEACON).ready.exists and self.units(STARGATE).ready.exists:
			if self.supply_left <15 and not self.already_pending(PYLON):
				nexuses = self.units(NEXUS).ready
				if nexuses.exists:
					if self.can_afford(PYLON):
						await self.build(PYLON, near= nexuses.first)
		else:			
			if self.supply_left <5 and not self.already_pending(PYLON):
				nexuses = self.units(NEXUS).ready
				if nexuses.exists:
					if self.can_afford(PYLON):
						await self.build(PYLON, near= nexuses.first)

	async def build_gas(self):
		for nexus in self.units(NEXUS).ready:
			vespenes = self.state.vespene_geyser.closer_than(15.0, nexus)
			for vespene in vespenes:
				if not self.can_afford(ASSIMILATOR):
					break
				worker = self.select_build_worker(vespene.position)
				if (worker) is None:
					break
				if not self.units(ASSIMILATOR).closer_than(1.0,vespene).exists:
					await self.do(worker.build(ASSIMILATOR, vespene))

	async def smart_expand(self):
		if self.units(NEXUS).amount < 4 and self.can_afford(NEXUS):
			await self.expand_now()

	async def army_buildings(self):
		

		if self.units(PYLON).ready.exists:
			pylon = self.units(PYLON).ready.random


			if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE).ready.exists:
					if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
						await self.build(CYBERNETICSCORE, near =pylon)
			elif self.units(GATEWAY).amount <1:
				if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
					await self.build(GATEWAY, near= pylon)
			
			if self.units(CYBERNETICSCORE).ready.exists:
				if self.units(STARGATE).ready.exists and not self.units(FLEETBEACON).ready.exists:
					if self.can_afford(FLEETBEACON) and not self.already_pending(FLEETBEACON):
						await self.build(FLEETBEACON, near=pylon)

				elif self.units(STARGATE).amount <(self.iteration/self.ITERATIONS_PER_MIN)/3:
					if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
						await self.build(STARGATE, near= pylon)

				if self.units(ROBOTICSFACILITY).amount < 1:
					if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
						await self.build(ROBOTICSFACILITY, near =pylon)

			



	async def army_units(self):
		#for gw in self.units(GATEWAY).ready.noqueue:
		#	if self.can_afford(STALKER) and self.supply_left>2:
		#		await self.do(gw.train(STALKER))

		for sg in self.units(STARGATE).ready.noqueue:
			if self.units(FLEETBEACON).ready.exists:
				if self.can_afford(CARRIER) and self.supply_left>6:
					await self.do(sg.train(CARRIER))
			#else:
			#	if self.can_afford(VOIDRAY) and self.supply_left>3:
			#		await self.do(sg.train(VOIDRAY))



	def find_target(self, state):
		if len(self.known_enemy_units)>0:
			return random.choice(self.known_enemy_units)
		elif len(self.known_enemy_structures) >0:
			return random.choice(self, known_enemy_structures)
		else:
			return self.enemy_start_locations[0]

	async def attack(self):
		aggro_units = {
			#STALKER: [15,5], 
			#VOIDRAY:[8,0], 
			CARRIER:[6,1]
			}

		if self.units(CARRIER).idle.amount >0:

			target = False
			if self.iteration> self.wait_duration:
				if self.use_model:
					prediction = self.model.predict([self.flipped.reshape([-1, 176, 200,3])])
					choice = np.argmax(prediction[0])
					choice_dict = {0: "No Attack!",
								   1: "Attack close to our nexus!",
								   2: "Attack Enemy Structure!",
								   3: "Attack Enemy Start Location!"}
					print("Choice #{}:{}".format(choice, choice_dict[choice]))
				else:
					choice = random.randrange(0,4)
			

			
			target = False

			if self.iteration > self.wait_duration:
				if choice ==0:
					#no attack
					wait = random.randrange(20,165)
					self.wait_duration = self.iteration + wait

				elif choice ==1:
					#attack closest nexus
					if self.known_enemy_units.amount>0:

						target = self.known_enemy_units.closest_to(random.choice(self.units(NEXUS)))

				elif choice ==2:
					#attack enemy buildings
					if self.known_enemy_structures.amount>0:

						target = seslf.known_enemy_units.closest_to(random_choice(self.units(NEXUS)))

				elif choice ==2:
					#attack enemy buildings
					if self.known_enemy_structures>0:

						target = random.choice(self.known_enemy_structures)

				elif choice ==3:
					#attack enemy starting location
					target = self.enemy_start_locations[0]

				if target:
					for carrier in self.units(CARRIER).idle:
						await self.do(carrier.attack(target))

				y = np.zeros(4)
				y[choice]=1
				print(y)
				self.train_data.append([y, self.flipped])


		#old code for mega stupid aggro
		#for UNIT in aggro_units:
		#	for mob in self.units(UNIT).idle:
		#		await self.do(mob.attack(self.find_target(self.state)))

		#old code for 2 types of scenarios, defend/attack
		#attack if have a lot of units
		#for UNIT in aggro_units:
		#	if self.units(UNIT).exists:
		#		if self.units(UNIT).amount > aggro_units[UNIT][0] and self.units(UNIT).amount > aggro_units[UNIT][1]:
		#			for mob in self.units(UNIT).idle:
		#				await self.do(mob.attack(self.find_target(self.state)))
			#defend if have fewer units
		#		elif self.units(UNIT).amount > aggro_units[UNIT][1]:
		#			if len(self.known_enemy_units)>0:
		#				for mob in self.units(UNIT).idle:
		#					await self.do(mob.attack(random.choice(self.known_enemy_units)))
				

		#if self.units(STALKER).amount > 15:
		#	for s in self.units(STALKER).idle:
		#		await self.do(s.attack(self.find_target(self.state)))


		#defend if have few units
		#elif self.units(STALKER).amount >4:
		#	if len(self.known_enemy_units)>0:
		#		for s in self.units(STALKER).idle:
		#			await self.do(s.attack(random.choice(self.known_enemy_units)))



	def random_location_variance(self, enemy_start_location):
		x = enemy_start_location[0]
		y = enemy_start_location[1]

		x+= ((random.randrange(-20, 20))/100) * enemy_start_location[0]
		y+= ((random.randrange(-20, 20))/100) * enemy_start_location[1]

		if x<0:
			x=0
		if y<0:
			y=0
		if x>self.game_info.map_size[0]:
			x= self.game_info.map_size[0]
		if y>self.game_info.map_size[1]:
			y= self.game_info.map_size[1]
		res = position.Point2(position.Pointlike((x,y)))
		return res

	async def scout(self):
		if self.units(OBSERVER).amount >0:
			scout = self.units(OBSERVER).random
			if scout.is_idle:
				enemy_location = self.enemy_start_locations[0]
				move_to = self.random_location_variance(enemy_location)
				await self.do(scout.move(move_to))
		elif self.units(OBSERVER).amount <1:
			for rf in self.units(ROBOTICSFACILITY).ready.noqueue:
				if self.can_afford(OBSERVER):
					await self.do(rf.train(OBSERVER))


for i in range(100):
	run_game(maps.get("AbyssalReefLE"), [
		Bot(Race.Protoss, MyProtossBot(use_model=True)),
		Computer(Race.Zerg, Difficulty.Medium)
		], realtime=False)


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, MyProtossBot()),
    Computer(Race.Terran, Difficulty.Hard)
    ], realtime=False)

