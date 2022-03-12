
import simpy
import random
import statistics

RANDOM_SEED = 10

def program(name, env, cpu, ram, io, instructions, velocity):
    global total
    global tiempos
    cant_memory = random.randint(1,10)

    print('%s llegando al SO en %f necesita %d de memoria' % (name, env.now, cant_memory))
    start = env.now

    #Cola memoria
    yield ram.get(cant_memory)

    print('%s asignado en espacio de memoria en %f' % (name, env.now))
    print('Espacio en memoria actual: %s' % (ram.level))
    state=2

    while(state!=0):

        if(state==2):
            with cpu.request() as req_cpu:
                print('%s en estado "ready", contiene %d instrucciones' % (name, instructions))
                yield req_cpu

                print('%s en estado "running" en %f' % (name, env.now))
                yield env.timeout(1)

                if (instructions < velocity):
                    instructions = 0
                else:
                    instructions = instructions - velocity

                print('%s sale de cpu a las %f' % (name, env.now))
                if (instructions != 0):
                    state = random.randint(1, 2)

        elif(state==1):
            with io.request() as req_io:
                print('%s en estado "waiting", contiene %d instrucciones' % (name, instructions))
                yield req_cpu
                yield env.timeout(random.randint(1,5))

                print('%s sale de la cola "waiting" a las %f' % (name, env.now))
                state = 2

        if(instructions==0):
            state=0
            print('%s en estado "terminated" en %f' % (name, env.now))

    print('%s desasignado en espacio de memoria en %f' % (name, env.now))
    print('Espacio en memoria actual: %s' % (ram.level+cant_memory))
    yield ram.put(cant_memory)

    tiempo = env.now - start
    tiempos.append(tiempo)
    print('%s ha tardado %f en ejecucion' % (name, tiempo))
    total = total + tiempo


def program_generator(env, cpu, ram, io, n, interval, velocity):
    """Generacion de nuevos programas"""
    for i in range(n):
        yield env.timeout(random.expovariate(1.0/interval))

        #Proceso de creacion de programa
        env.process(program('Programa %d' %i, env, cpu, ram, io, random.randint(1,10), velocity))


env = simpy.Environment() #ambiente de simulacion

cpu = simpy.Resource(env, capacity=1) #CPU como recurso a compartir
io = simpy.Resource(env, capacity=1) #I/O como recurso a compartir

ram = simpy.Container(env, init=100, capacity=100) #RAM como contenedor

random.seed(RANDOM_SEED)


#Solicitud de datos de ingreso
print('Ingrese la cantidad de procesos: ')
n = input()

print('Ingrese el intervale de llegada: ')
interval = input()

print('Ingrese la velocidad del cpu: ')
velocity = input()

total = 0
tiempos = []

#Proceso de creacion de programas
env.process(program_generator(env,cpu,ram, io, int(n), int(interval), int(velocity)))
env.run()
print ("Tiempo promedio por proceso es: ", total/int(n))
print ("Desviacion estandar del tiempo por proceso es: ", statistics.stdev(tiempos))