import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
CYBERNETICSCORE, STALKER, ZEALOT, STARGATE, VOIDRAY, CARRIER, FLEETBEACON
import random


class MyProtossBot(sc2.BotAI):
	def __init__(self):
		self.ITERATIONS_PER_MIN = 165
		self.MAX_WORKERS= 65
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
			elif self.units(GATEWAY).amount <(self.iteration/self.ITERATIONS_PER_MIN)/4:
				if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
					await self.build(GATEWAY, near= pylon)
			
			if self.units(CYBERNETICSCORE).ready.exists:
				if self.units(STARGATE).ready.exists and not self.units(FLEETBEACON).ready.exists:
					if self.can_afford(FLEETBEACON) and not self.already_pending(FLEETBEACON):
						await self.build(FLEETBEACON, near=pylon)

				elif self.units(STARGATE).amount <(self.iteration/self.ITERATIONS_PER_MIN)/3:
					if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
						await self.build(STARGATE, near= pylon)
			



	async def army_units(self):
		for gw in self.units(GATEWAY).ready.noqueue:
			if self.can_afford(STALKER) and self.supply_left>2:
				await self.do(gw.train(STALKER))

		for sg in self.units(STARGATE).ready.noqueue:
			if self.units(FLEETBEACON).ready.exists:
				if self.can_afford(CARRIER) and self.supply_left>6:
					await self.do(sg.train(CARRIER))
			else:
				if self.can_afford(VOIDRAY) and self.supply_left>3:
					await self.do(sg.train(VOIDRAY))



	def find_target(self, state):
		if len(self.known_enemy_units)>0:
			return random.choice(self.known_enemy_units)
		elif len(self.known_enemy_structures) >0:
			return random.choice(self, known_enemy_structures)
		else:
			return self.enemy_start_locations[0]

	async def attack(self):
		aggro_units = {STALKER: [15,5], VOIDRAY:[8,0], CARRIER:[6,1]}
		#attack if have a lot of units
		for UNIT in aggro_units:
			if self.units(UNIT).exists:
				if self.units(UNIT).amount > aggro_units[UNIT][0] and self.units(UNIT).amount > aggro_units[UNIT][1]:
					for mob in self.units(UNIT).idle:
						await self.do(mob.attack(self.find_target(self.state)))
			#defend if have fewer units
				elif self.units(UNIT).amount > aggro_units[UNIT][1]:
					if len(self.known_enemy_units)>0:
						for mob in self.units(UNIT).idle:
							await self.do(mob.attack(random.choice(self.known_enemy_units)))
				

		#if self.units(STALKER).amount > 15:
		#	for s in self.units(STALKER).idle:
		#		await self.do(s.attack(self.find_target(self.state)))


		#defend if have few units
		#elif self.units(STALKER).amount >4:
		#	if len(self.known_enemy_units)>0:
		#		for s in self.units(STALKER).idle:
		#			await self.do(s.attack(random.choice(self.known_enemy_units)))





run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, MyProtossBot()),
    Computer(Race.Terran, Difficulty.Hard)
    ], realtime=False)