
import simpy
import random
import statistics

RANDOM_SEED = 10

def program(name, env, cpu, ram, io, instructions, velocity, llegada):
    global total
    global tiempos
    cant_memory = random.randint(1,10)

    yield env.timeout(llegada)

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


env = simpy.Environment() #ambiente de simulacion

#Solicitud de datos de ingreso
print('Ingrese la cantidad de procesos: ')
n = input()

print('Ingrese el intervale de llegada: ')
interval = input()

print('Ingrese las instrucciones/unidad de tiempo del cpu: ')
velocity = input()

print('Ingrese la capacidad de la RAM: ')
ram_capacity = input()

print('Ingrese la cantidad de CPUs: ')
cpu_capacity = input()

total = 0
tiempos = []

cpu = simpy.Resource(env, capacity=int(cpu_capacity)) #CPU como recurso a compartir
io = simpy.Resource(env, capacity=1) #I/O como recurso a compartir

ram = simpy.Container(env, init=int(ram_capacity), capacity=int(ram_capacity)) #RAM como contenedor

random.seed(RANDOM_SEED)

#Proceso de creacion de programas
for i in range(int(n)):
    llegada = random.expovariate(1.0/int(interval))
    env.process(program('Programa %d' % i, env, cpu, ram, io, random.randint(1,10), int(velocity), llegada))

env.run()
print ("Tiempo promedio por proceso es: ", total/int(n))
print ("Desviacion estandar del tiempo por proceso es: ", statistics.stdev(tiempos))