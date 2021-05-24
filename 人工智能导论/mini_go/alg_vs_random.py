from absl import logging, flags, app
from environment.GoEnv import Go
import time, os
import numpy as np
import tensorflow as tf
from algorithms.policy_gradient import PolicyGradient
from algorithms.dqn import DQN
import agent.agent as agent
def get_max_idx(path):
    all_models = []
    for i in list(os.walk(path))[-1][-1]:
        all_models.append(i.split(".")[0])
    max_idx = max([eval(i) for i in all_models if i.isdigit()])

    return max_idx

FLAGS = flags.FLAGS

flags.DEFINE_integer("num_train_episodes", 100000,
                     "Number of training episodes for each base policy.")
flags.DEFINE_integer("num_eval", 1000,
                     "Number of evaluation episodes")
flags.DEFINE_integer("eval_every", 2000,
                     "Episode frequency at which the agents are evaluated.")
flags.DEFINE_integer("learn_every", 128,
                     "Episode frequency at which the agents learn.")
flags.DEFINE_integer("save_every", 5000,
                     "Episode frequency at which the agents save the policies.")
flags.DEFINE_list("hidden_layers_sizes", [
    128, 128
], "Number of hidden units in the net.")
flags.DEFINE_integer("replay_buffer_capacity", int(5e4),
                     "Size of the replay buffer.")
flags.DEFINE_integer("reservoir_buffer_capacity", int(2e6),
                     "Size of the reservoir buffer.")
flags.DEFINE_bool("use_dqn",bool(True),"use dqn or not. If set to false, use a2c")

def use_dqn():
    return FLAGS.use_dqn 

def init_env():
    begin = time.time()
    env = Go(flatten_board_state=True)
    info_state_size = env.state_size
    num_actions = env.action_size

    return env,info_state_size,num_actions, begin

def init_hyper_paras():
    hidden_layers_sizes = [int(l) for l in FLAGS.hidden_layers_sizes]
    kwargs = {
        "replay_buffer_capacity": FLAGS.replay_buffer_capacity,
        "epsilon_decay_duration": int(0.6*FLAGS.num_train_episodes),
        "epsilon_start": 0.8,
        "epsilon_end": 0.001,
        "learning_rate": 3e-4,
        "learn_every": FLAGS.learn_every,
        "batch_size": 128,
        "max_global_gradient_norm": 10,
    }
    ret = [0]
    max_len = 2000

    return hidden_layers_sizes, kwargs, ret, max_len

def init_agents(sess,info_state_size,num_actions,hidden_layers_sizes,**kwargs):
    agents = [DQN(sess, 0, info_state_size,
                        num_actions, hidden_layers_sizes, **kwargs), agent.RandomAgent(1)]
    sess.run(tf.global_variables_initializer())

    return agents 

def prt_logs(ep,agents,ret,begin):

    losses = agents[0].loss
    logging.info("Episodes: {}: Losses: {}, Rewards: {}".format(ep + 1, losses, np.mean(ret)))
    with open('logs/log_{}_{}'.format(os.environ.get('BOARD_SIZE'), "dqn_vs_rand"), 'a+') as log_file:
        log_file.writelines("{}, {}\n".format(ep+1, np.mean(ret)))

def save_model(ep,agents):

    if not os.path.exists("saved_model"):
        os.mkdir('saved_model')
    agents[0].save(checkpoint_root='saved_model', checkpoint_name='{}'.format(ep+1))

    print("Model Saved!")

def restore_model(agents,path=None):

    if path:
        agents[0].restore(path)
        idex = path.split("/")[-1]
    else:
        idex = get_max_idx("./saved_model")
        path = os.path.join("./saved_model/",str(idex))
        agents[0].restore(path)

    logging.info("Agent model restored at {}".format(path))

    return int(idex)


def train(agents,env,ret,max_len,begin):

    global_ep = restore_model(agents)
    # global_ep = restore_model(agents,"./used_model/38000")

    try:

        for ep in range(FLAGS.num_train_episodes):

            if (ep + 1) % FLAGS.eval_every == 0:

                prt_logs(global_ep+ep,agents,ret,begin)

            if (ep + 1) % FLAGS.save_every == 0:

                save_model(global_ep+ep,agents)

            time_step = env.reset()  # a go.Position object

            while not time_step.last():

                player_id = time_step.observations["current_player"]
                agent_output = agents[player_id].step(time_step)
                action_list = agent_output.action
                time_step = env.step(action_list)

            for agent in agents:

                agent.step(time_step)

            if len(ret) < max_len:

                ret.append(time_step.rewards[0])

            else:

                ret[ep % max_len] = time_step.rewards[0]

    except KeyboardInterrupt:

        save_model(global_ep+ep,agents)

def evaluate(agents,env):

    # global_ep = restore_model(agents)
    logging.info("Evaluation Begins...")
    global_ep = restore_model(agents,"./used_model/146000")

    ret = []

    for ep in range(FLAGS.num_eval):
        time_step = env.reset()
        while not time_step.last():
            player_id = time_step.observations["current_player"]
            if player_id == 0:
                agent_output = agents[player_id].step(time_step, is_evaluation=True, add_transition_record=False)
            else:
                agent_output = agents[player_id].step(time_step)
            action_list = agent_output.action
            time_step = env.step(action_list)

        # Episode is over, step all agents with final info state.
        # for agent in agents:
        agents[0].step(time_step, is_evaluation=True, add_transition_record=False)
        agents[1].step(time_step)
        ret.append(time_step.rewards[0])    

    return ret 

def stat(ret,begin):

    print(np.mean(ret))

    print('Time elapsed:', time.time()-begin)


def main(unused_argv):

    env, info_state_size,num_actions, begin = init_env()
    hidden_layers_sizes, kwargs, ret, max_len = init_hyper_paras()

    with tf.Session() as sess:

        agents = init_agents(sess,info_state_size,num_actions,hidden_layers_sizes,**kwargs)

        # train(agents,env,ret,max_len, begin)

        ret = evaluate(agents,env)

        stat(ret,begin)

if __name__ == '__main__':
    app.run(main)
