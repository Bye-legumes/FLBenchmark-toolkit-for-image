from time import sleep
from multiprocessing import Process, Pipe
import random
import json
import flmedbenchmark.datasets
import flmedbenchmark.logging

config = json.load(open('/test/config.json', 'r'))

flbd = flmedbenchmark.datasets.FLBDatasets('/data')

train_dataset, test_dataset = flbd.fateDatasets(config['dataset'])

if len(train_dataset.parties) != 2:
    raise NotImplementedError('The demo only supports 2 clients.')


def client(id, pipe):
    logger = flmedbenchmark.logging.Logger(id=id, agent_type='client', dir='/test/log')
    # Log the data processing
    with logger.preprocess_data():
        sleep(0.3)
        weights = [0.1, 0.2]
    # Log the training process
    with logger.training():
        for i in range(config['training_param']['epochs']):
            # Log every training round
            with logger.training_round() as t:
                t.report_metric('client_num', 2)  # Report the number of clients in this round
                # Log the computation
                with logger.computation() as c:
                    sleep(random.random())  # Simulate the computation
                    weights = [random.random(), random.random()]  # Get the gradient
                    c.report_metric('flop', 123)  # Report the cost of this computation
                    c.report_metric('loss', 0.8)  # Report loss
                # Upload the gradient
                with logger.communication(target_id=0) as c:
                    pipe.send(weights)  # Simulate the network communication
                    c.report_metric('byte', 1234)  # Report the cost of this communication
                # Wait for the new model
                weights = pipe.recv()
    # End the logging
    logger.end()


def client2(id, pipe):
    logger = flmedbenchmark.logging.Logger(id=id, agent_type='client')
    # Log the data processing
    logger.preprocess_data_start()
    sleep(0.3)
    weights = [0.1, 0.2]
    logger.preprocess_data_end()
    # Log the training process
    logger.training_start()
    for i in range(config['training_param']['epochs']):
        # Log every training round
        logger.training_round_start()
        # Log the computation
        logger.computation_start()
        sleep(random.random())  # Simulate the computation
        weights = [random.random(), random.random()]  # Get the gradient
        logger.computation_end(metrics={'flop': 123, 'loss': 0.8})  # Report the cost of this computation and loss
        # Upload the gradient
        logger.communication_start(target_id=0)
        pipe.send(weights)  # Simulate the network communication
        logger.communication_end(metrics={'byte': 1234})  # Report the cost of this communication
        # Wait for the new model
        weights = pipe.recv()
        logger.training_round_end(metrics={'client_num': 2})  # Report the number of clients in this round
    logger.training_end()
    # End the logging
    logger.end()


def aggregator(id, pipe1, pipe2):
    with flmedbenchmark.logging.Logger(id=id, agent_type='aggregator') as logger:
        weights = [0.0, 0.0]
        with logger.training():
            for i in range(config['training_param']['epochs']):
                # Log every training round
                with logger.training_round():
                    # Wait for the gradients from clients
                    w1 = pipe1.recv()
                    w2 = pipe2.recv()
                    # Average the gradients
                    with logger.computation() as c:
                        sleep(random.random())  # Simulate the computation
                        weights = [(w1[0]+w2[0])/2, (w1[1]+w2[1])/2]  # Average the gradients
                        c.report_metric('flop', 123)  # Report the cost
                    # Distribute the new model
                    with logger.communication(target_id=1) as c:
                        pipe1.send(weights)  # Simulate the network communication
                        c.report_metric('byte', 1234)  # Report the cost
                    with logger.communication(target_id=2) as c:
                        pipe2.send(weights)  # Simulate the network communication
                        c.report_metric('byte', 1234)  # Report the cost
        # Model evaluation
        with logger.model_evaluation() as e:
            sleep(0.1)
            e.report_metric('accuracy', 99.9)


# 2 clients, 1 aggregator
if __name__ == '__main__':
    (pipe_0_1, pipe_0_2) = Pipe()
    (pipe_1_1, pipe_1_2) = Pipe()
    a0 = Process(target=aggregator, args=(0, pipe_0_1, pipe_1_1))
    c1 = Process(target=client, args=(1, pipe_0_2))
    c2 = Process(target=client2, args=(2, pipe_1_2))
    a0.start()
    c1.start()
    c2.start()
    a0.join()
    c1.join()
    c2.join()
