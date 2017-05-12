import sys
import math
import pygame
import random
import time
import importlib
from pygame.locals import *
from pygame.color import *
				
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util
import visionField


GLADIATOR_COLLISION = 1
ENEMY_COLLISION = 2
GLADIATOR_BULLET = 3
ENEMY_BULLET = 4
WALL_COLLISION = 5
gladiator_shot = False
enemy_shot = False
gladiator_win = False
enemy_win = False
collision = True

def create_bullet(robot):
	vs = [(-30,0), (0,3), (10,0), (0,-3)]
	mass = 1
	moment = pymunk.moment_for_circle(mass, 0, 3, (0,0))
	g_bullet_body = pymunk.Body(mass, moment)
	
	g_bullet_shape = pymunk.Circle(g_bullet_body, 3)
	g_bullet_shape.color = (47, 79, 79)
	g_bullet_shape.friction = 5.
	g_bullet_shape.elasticity = 0

	if robot == "gladiator":
		g_bullet_shape.collision_type = GLADIATOR_BULLET
	elif robot == "enemy":
		g_bullet_shape.collision_type = ENEMY_BULLET

	return g_bullet_body, g_bullet_shape


def post_solve_robots_hit(arbiter, space, data):
	global collision
	#if arbiter.total_impulse.lenght > 10:
	collision = True



def post_solve_wall_hit_g(arbiter, space, data):
	if arbiter.total_impulse.length > 10:
		global gladiator_shot
		a,b = arbiter.shapes
		position = arbiter.contact_point_set.points[0].point_a
		b.collision_type = 0
		b.group = 1
		other_body = a.body
		g_bullet_body = b.body
		space.remove(b)
		space.remove(g_bullet_body)
		gladiator_shot = False

def post_solve_wall_hit_e(arbiter, space, data):
	if arbiter.total_impulse.length > 10:
		global enemy_shot
		a,b = arbiter.shapes
		position = arbiter.contact_point_set.points[0].point_a
		b.collision_type = 0
		b.group = 1
		other_body = a.body
		e_bullet_body = b.body
		space.remove(b)
		space.remove(e_bullet_body)
		enemy_shot = False

def post_solve_gladiator_hit(arbiter, space, data):
	if arbiter.total_impulse.length > 50:
		global gladiator_shot, gladiator_win
		a,b = arbiter.shapes
		position = arbiter.contact_point_set.points[0].point_a
		b.collision_type = 0
		b.group = 1
		other_body = a.body
		g_bullet_body = b.body
		space.remove(b)
		space.remove(g_bullet_body)
		gladiator_shot = False
		gladiator_win = True

def post_solve_enemy_hit(arbiter, space, data):
	if arbiter.total_impulse.length > 50:
		global enemy_shot, enemy_win
		a,b = arbiter.shapes
		position = arbiter.contact_point_set.points[0].point_a
		b.collision_type = 0
		b.group = 1
		other_body = a.body
		e_bullet_body = b.body
		space.remove(b)
		space.remove(e_bullet_body)
		enemy_shot = False
		enemy_win = True


def runaway_bullet(bullet_pos):
	if bullet_pos.x > 880 or bullet_pos.x < 30:
		return True
	elif bullet_pos.y > 620 or bullet_pos.y < 30:
		return True
	else:
		return False

def gladiator_velocity(body, gravity, damping, dt):
	body.velocity =  Vec2d(1,0).rotated(body.angle).normalized() * 150

def enemy_velocity(body, gravity, damping, dt):
	body.velocity =  Vec2d(1,0).rotated(body.angle).normalized() * 150

def bullet_velocity(body, gravity, damping, dt):	
	body.velocity = body.velocity.normalized() * 300

def calculate_fov(body, fov, fov_shooting):
	segment1_angle = 0
	segment2_angle = 0
	segment3_angle = 0
	segment4_angle = 0
	if body.angle >= 0 and body.angle <= math.pi:
		segment1_angle = body.angle + fov/2
		segment2_angle = body.angle - fov/2
		segment3_angle = body.angle + fov_shooting/2
		segment4_angle = body.angle - fov_shooting/2
	elif body.angle >= -math.pi and body.angle <= 0:
		segment1_angle = body.angle - fov/2
		segment2_angle = body.angle + fov/2
		segment3_angle = body.angle - fov_shooting/2
		segment4_angle = body.angle + fov_shooting/2

	segment1_beg = body.position + Vec2d(0, 0).rotated(body.angle)
	segment2_beg = body.position + Vec2d(0, 0).rotated(body.angle)
	segment1_end = body.position + Vec2d(300, 0).rotated(segment1_angle)		
	segment2_end = body.position + Vec2d(300, 0).rotated(segment2_angle)

	segment3_beg = body.position + Vec2d(0, 0).rotated(body.angle)
	segment4_beg = body.position + Vec2d(0, 0).rotated(body.angle)
	segment3_end = body.position + Vec2d(300, 0).rotated(segment3_angle)		
	segment4_end = body.position + Vec2d(300, 0).rotated(segment4_angle)

	return [segment1_beg, segment2_beg, segment3_beg, segment4_beg, segment1_end, segment2_end, segment3_end, segment4_end]

def change_angle(action, body):
	if action == 1:
		if body.angle >= -math.pi and body.angle <= 0:
			body.angle -= 0.08
			if body.angle < -math.pi:
				error = abs(body.angle+math.pi)
				body.angle = math.pi - (error+0.1)
		else:
			body.angle -= 0.08
	elif action == 2:			
		if body.angle <= math.pi and body.angle >= 0:
			body.angle += 0.08
			if body.angle > math.pi:
				error = abs(body.angle-math.pi)
				body.angle = -math.pi + (error+0.1)
		else:
			body.angle += 0.08

def random_spawn(robot):
	if robot == "gladiator":
		y = random.randint(100, 530)
		position = (700, y)
		angle = random.uniform(math.pi/2, -math.pi/2)

	elif robot == "enemy":
		y = random.randint(100, 530)
		position = (200, y)
		angle = random.uniform(math.pi/2, -math.pi/2)

	return position, angle

def compute_performance(survival_time, max_time, hit_time):
	return (0.5 * (survival_time/max_time) + 0.5 * ( (max_time-hit_time) / max_time)) - 0.5

def create_robot(color, robot):
	robot_mass =  1
	robot_radius = 15
	robots_inertia = pymunk.moment_for_circle(robot_mass, 0, robot_radius, (0,0))

	robot_body = pymunk.Body(robot_mass, robots_inertia)
	robot_body.position, robot_body.angle = random_spawn(robot)
	robot_shape = pymunk.Circle(robot_body, robot_radius, (0,0))
	robot_shape.elasticity = 0
	robot_shape.friction = 5.
	robot_shape.color = color

	if robot == "gladiator":
		robot_body.velocity_func = gladiator_velocity
		robot_shape.collision_type = GLADIATOR_COLLISION
	elif robot == "enemy":
		robot_body.velocity_func = enemy_velocity
		robot_shape.collision_type = ENEMY_COLLISION
	return robot_body, robot_shape

def parse_info(load_info):
    f = open(load_info, 'r')
    contents = f.readlines()

    return contents[0].rstrip('\n'), contents[1].rstrip('\n')


width, height = 900, 650
def versus(AI1, AI2):
	P1 = importlib.import_module(AI1)
	P2 = importlib.import_module(AI2)
	global gladiator_shot, enemy_shot, gladiator_win, enemy_win, gladiator_speed, enemy_speed, collision

	##inicializa o pygame
	episode = 0

	pygame.init()
	window = pygame.display.set_mode((width,height))
	font = pygame.font.SysFont("System", 20)
	font2 = pygame.font.SysFont("monospace", 20)

	#background
	bg = pygame.image.load("./resources/bg.jpg")
	bg = pygame.transform.scale(bg, (width,height))
	bg.set_alpha(200)

	#wall
	wall = pygame.image.load("./resources/border.png")
	wall_updown = pygame.transform.rotate(wall, 90)
	wall_updown = pygame.transform.scale(wall_updown, (10 ,561))
	wall_leftright = pygame.transform.scale(wall, (811, 10))

	#robos
	robo1 = pygame.image.load("./resources/robo1.png")
	robo1 = pygame.transform.scale(robo1, (30,30))

	robo2 = pygame.image.load("./resources/robo2.png")
	robo2 = pygame.transform.scale(robo2, (30,30))

	#tiro
	tiro1 = pygame.image.load("./resources/shot.png")
	tiro1 = pygame.transform.scale(tiro1, (9,9))

	tiro2 = pygame.image.load("./resources/shot.png")
	tiro2 = pygame.transform.scale(tiro2, (9,9))

	state = P1.State(1,False,1,False)
	player1, load1 = parse_info("./" + AI1 + "/group_info")
	player1 = player1.strip("\n")
	player2, load2 = parse_info("./" + AI2 + "/group_info")
	player2 = player2.strip("\n")
	controller1 = P1.Controller("./" + AI1 + "/" + load1, state)
	controller2 = P2.Controller("./" + AI2 + "/" + load2, state)

	fov = math.pi/4
	fov_shooting = fov/3
	player1_score = 0
	player2_score = 0
	draws = 0
	perf1 = 0
	perf2 = 0

	while(episode < 13):
		perf = 0
		gladiator_shot = False
		enemy_shot = False
		gladiator_win = False
		enemy_win = False
		collision = False
		clock = pygame.time.Clock() 
		running = True

		#configura espaco de simulacao do pymunk
		space = pymunk.Space()
		space.gravity = 0, 0

		draw_options = pymunk.pygame_util.DrawOptions(window)

		#paredes          
		static = [pymunk.Segment(space.static_body, (50, 50), (50, 600), 5)
								,pymunk.Segment(space.static_body, (50, 600), (850, 600), 5)
								,pymunk.Segment(space.static_body, (850, 600), (850, 50), 5)
								,pymunk.Segment(space.static_body, (50, 50), (850, 50), 5)
								]
		for s in static:
			s.friction = 0.
			s.elasticity = 10.
			s.group = 1
			s.collision_type = WALL_COLLISION
		space.add(static)

		###define o corpo/forma de cada um dos robos
		gladiator_body, gladiator_shape = create_robot((45, 100, 245), "gladiator")
		space.add(gladiator_body, gladiator_shape)
		enemy_body, enemy_shape = create_robot((161, 40, 48), "enemy")
		space.add(enemy_body, enemy_shape)


		#handlers de colisoes
		collision_handler1 = space.add_collision_handler(ENEMY_COLLISION, GLADIATOR_BULLET)
		collision_handler1.post_solve = post_solve_gladiator_hit

		collision_handler2 = space.add_collision_handler(GLADIATOR_COLLISION, ENEMY_BULLET)
		collision_handler2.post_solve = post_solve_enemy_hit

		collision_handler3 = space.add_collision_handler(WALL_COLLISION, GLADIATOR_BULLET)
		collision_handler3.post_solve = post_solve_wall_hit_g

		collision_handler4 = space.add_collision_handler(WALL_COLLISION, ENEMY_BULLET)
		collision_handler4.post_solve = post_solve_wall_hit_e

		collision_handler5 = space.add_collision_handler(GLADIATOR_COLLISION, ENEMY_COLLISION)
		collision_handler5.post_solve = post_solve_robots_hit

		g_bullet_body = None
		e_bullet_body = None
		beg_time = time.time()
		actions = 0
		e_forward = 0

		while running:

			for event in pygame.event.get():
				if event.type == QUIT or event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
					running = False
					episode = 15

			if g_bullet_body != None:
				g_bullet_vector = [g_bullet_body.position.x - enemy_body.position.x, g_bullet_body.position.y - enemy_body.position.y]
				if runaway_bullet(g_bullet_body.position) == True:
					gladiator_shot = False
			if e_bullet_body != None:			
				e_bullet_vector = [e_bullet_body.position.x - gladiator_body.position.x, e_bullet_body.position.y - gladiator_body.position.y]
				if runaway_bullet(e_bullet_body.position) == True:
					enemy_shot = False


			g_segments = calculate_fov(gladiator_body, fov, fov_shooting)
			e_segments = calculate_fov(enemy_body, fov, fov_shooting)

			enemyVector = [enemy_body.position.x - gladiator_body.position.x, enemy_body.position.y - gladiator_body.position.y]
			gladiatorVector = [gladiator_body.position.x - enemy_body.position.x, gladiator_body.position.y - enemy_body.position.y]

			gl_innerVector = [g_segments[6].x - gladiator_body.position.x, g_segments[6].y - gladiator_body.position.y]
			gr_innerVector = [g_segments[7].x - gladiator_body.position.x, g_segments[7].y - gladiator_body.position.y] 
			el_innerVector = [e_segments[6].x - enemy_body.position.x, e_segments[6].y - enemy_body.position.y]
			er_innerVector = [e_segments[7].x - enemy_body.position.x, e_segments[7].y - enemy_body.position.y] 

			gl_outerVector = [g_segments[4].x - gladiator_body.position.x, g_segments[4].y - gladiator_body.position.y]
			gr_outerVector = [g_segments[5].x - gladiator_body.position.x, g_segments[5].y - gladiator_body.position.y]
			el_outerVector = [e_segments[4].x - enemy_body.position.x, e_segments[4].y - enemy_body.position.y]
			er_outerVector = [e_segments[5].x - enemy_body.position.x, e_segments[5].y - enemy_body.position.y]

			dist_enemy = math.hypot(gladiator_body.position.x - enemy_body.position.x, gladiator_body.position.y - enemy_body.position.y)

			e_distance_to_bullet = 970.8
			e_bullet_in_fov = False
			if g_bullet_body != None and gladiator_shot == True:
				e_bullet_in_fov = visionField.inVisionCone(g_bullet_vector, el_outerVector, er_outerVector, visionField.rad2deg(fov))
				e_distance_to_bullet = math.hypot(g_bullet_body.position.x - enemy_body.position.x, g_bullet_body.position.y - enemy_body.position.y)

			g_distance_to_bullet = 970.8
			g_bullet_in_fov = False
			if e_bullet_body != None and enemy_shot == True:
				g_bullet_in_fov = visionField.inVisionCone(e_bullet_vector, gl_outerVector, gr_outerVector, visionField.rad2deg(fov))
				g_distance_to_bullet = math.hypot(e_bullet_body.position.x - gladiator_body.position.x, e_bullet_body.position.y - gladiator_body.position.y)


			enemy_in_fov = visionField.inVisionCone(enemyVector, gl_innerVector, gr_innerVector, visionField.rad2deg(fov_shooting))
			gladiator_in_fov = visionField.inVisionCone(gladiatorVector, el_innerVector, er_innerVector, visionField.rad2deg(fov_shooting))

			#trecho de invocacao da IA
			actions += 1

			action = controller1.take_action(
				P1.State(dist_enemy, int(enemy_in_fov), g_distance_to_bullet, int(g_bullet_in_fov)))
			
			controller1.state = P1.State(dist_enemy, int(enemy_in_fov), g_distance_to_bullet, int(g_bullet_in_fov))
			
			
			if action == 4 and gladiator_shot == False:
				rand = random.randrange(0,10)
				if rand > 5:
					angle_shift = random.uniform(0, fov_shooting/2)
				else:
					angle_shift = random.uniform(0, -fov_shooting/2)

				g_bullet_body, g_bullet_shape = create_bullet("gladiator")				
				g_bullet_body.position = gladiator_body.position + Vec2d(gladiator_shape.radius, 0).rotated(gladiator_body.angle)
				g_bullet_body.angle = gladiator_body.angle + angle_shift		
				g_bullet_body.velocity_func = bullet_velocity
				g_bullet_body.apply_impulse_at_local_point(Vec2d(1,0), g_bullet_body.position)
				space.add(g_bullet_body, g_bullet_shape)
				gladiator_bullet = g_bullet_body
				gladiator_shot = True
			else: 
				change_angle(action, gladiator_body)


			action = controller2.take_action(
				P1.State(dist_enemy, int(gladiator_in_fov), e_distance_to_bullet, int(e_bullet_in_fov)))

			controller2.state = P1.State(dist_enemy, int(gladiator_in_fov), e_distance_to_bullet, int(e_bullet_in_fov))
	
			if action == 4 and enemy_shot == False:
				rand = random.randrange(0,10)
				if rand > 5:
					angle_shift = random.uniform(0, fov_shooting/2)
				else:
					angle_shift = random.uniform(0, -fov_shooting/2)

				e_bullet_body, e_bullet_shape = create_bullet("enemy")				
				e_bullet_body.position = enemy_body.position + Vec2d(enemy_shape.radius, 0).rotated(enemy_body.angle)
				e_bullet_body.angle = enemy_body.angle + angle_shift		
				e_bullet_body.velocity_func = bullet_velocity
				e_bullet_body.apply_impulse_at_local_point(Vec2d(1,0), e_bullet_body.position)
				space.add(e_bullet_body, e_bullet_shape)
				enemy_bullet = e_bullet_body
				enemy_shot = True
			else:
				change_angle(action, enemy_body)

			if enemy_body.angle < -math.pi:
				enemy_body.angle = math.pi-0.05
			elif enemy_body.angle > math.pi:
				enemy_body.angle = -math.pi+0.05

			if gladiator_body.angle < -math.pi:
				gladiator_body.angle = math.pi-0.05
			elif gladiator_body.angle > math.pi:
				gladiator_body.angle = -math.pi+0.05
		

		
			#limpa tela
			window.fill(pygame.color.THECOLORS["black"])

			window.blit(bg,(0,0))

			#desenha paredes
			window.blit(wall_updown,(45,45))
			window.blit(wall_updown,(845,45))
			window.blit(wall_leftright,(45,595))
			window.blit(wall_leftright,(45,45))

			#desenha robos
			player_pos = gladiator_body.position
			window.blit(robo1,(player_pos.x-15,height-player_pos.y-15))

			enemy_pos = enemy_body.position
			window.blit(robo2,(enemy_pos.x-15,height-enemy_pos.y-15))

			
			#desenha tiros
			if g_bullet_body != None:
				g_bullet_pos = g_bullet_body.position
				if(g_bullet_pos.x > 60) and (g_bullet_pos.x < 830) and (g_bullet_pos.y > 60) and (g_bullet_pos.y < 580):
					window.blit(tiro1,(g_bullet_pos.x-9,height-g_bullet_pos.y-9))
			if e_bullet_body != None:
				e_bullet_pos = e_bullet_body.position
				if(e_bullet_pos.x > 60) and (e_bullet_pos.x < 830) and (e_bullet_pos.y > 60) and (e_bullet_pos.y < 580):
					window.blit(tiro2,(e_bullet_pos.x-9,height-e_bullet_pos.y-9))


			#desenha fov e sight na tela
			draw_options.draw_segment(g_segments[0], g_segments[4], (45, 100, 245))
			draw_options.draw_segment(g_segments[1], g_segments[5], (45, 100, 245))
			draw_options.draw_segment(g_segments[2], g_segments[6], (200, 200, 200))
			draw_options.draw_segment(g_segments[3], g_segments[7], (200, 200, 200))

			draw_options.draw_segment(e_segments[0], e_segments[4], (255, 0, 0))
			draw_options.draw_segment(e_segments[1], e_segments[5], (255, 0, 0))
			draw_options.draw_segment(e_segments[2], e_segments[6], (200, 200, 200))
			draw_options.draw_segment(e_segments[3], e_segments[7], (200, 200, 200))
			

			current_time = time.time() - beg_time

			#printa informacoes na tela
			window.blit(font.render("FPS: " + str(clock.get_fps()), 1, THECOLORS["green"]), (0,0))
			window.blit(font.render("Time: " + str(current_time), 1, THECOLORS["green"]), (0,15))
			window.blit(font.render("Press ESC or Q to quit", 1, THECOLORS["darkgrey"]), (5,height - 20))
			window.blit(font.render("Round " + str(episode) + " (" + str(draws) + " Empates)", 1, THECOLORS["green"]), (420,0))
			window.blit(font.render(player1 + " (azul): " + str(player1_score), 1, THECOLORS["green"]), (420,15))
			window.blit(font.render(player2 + " (vermelho): " + str(player2_score), 1, THECOLORS["green"]), (420,30))
			pygame.display.flip()

			actions = float(actions)
			if collision == True:
				perf += 0.0
				draws += 1
				print "Colisao: %f" % (perf)
				running = False
			elif gladiator_win == True:
				perf += compute_performance(900, 900, actions)	
				perf1 += perf
				player1_score += 1	
				print player1.strip("\n") + " venceu: " + str(perf)
				running = False
			elif enemy_win == True:
				perf += compute_performance(actions, 900, 900)
				perf2 += perf
				player2_score += 1
				print player2 + " venceu: " + str(-perf)
				running = False
			elif actions == 900:
				perf += compute_performance(actions, 900, 900)
				draws += 1
				print "Empate: %f" % (perf)
				running = False
			
			fps = 30
			dt = 1./fps
			space.step(dt)
			clock.tick(fps)
		episode += 1

	print "\nResultados:"
	print "\tRounds:"
	print "\t\t" + player1 + " " + str(player1_score) + " - "  + str(player2_score) + " " + player2
	print "\tPerformances (total):"
	print "\t\t" + player1 + " " + str(perf1)
	print "\t\t" + player2 + " " + str(-perf2)
	print "\tEmpates: "
	print "\t\t" + str(draws)

if __name__ == '__main__':
    sys.exit(game())



				

