import sys
sys.path.append("../")
from absl import logging, flags, app
from environment.GoEnv import Go
import time, os
import numpy as np
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from algorithms.policy_gradient import PolicyGradient
def get_max_idx(path):
    all_models = []
    for i in list(os.walk(path))[-1][-1]:
        all_models.append(i.split(".")[0])
    max_idx = max([eval(i) for i in all_models if i.isdigit()])

    return max_idx


FLAGS = flags.FLAGS

flags.DEFINE_integer("num_train_episodes", 200000,
                     "Number of training episodes for each base policy.")
flags.DEFINE_integer("num_eval", 1000,
                     "Number of evaluation episodes")
flags.DEFINE_integer("eval_every", 2000,
                     "Episode frequency at which the agents are evaluated.")
flags.DEFINE_integer("learn_every", 128,
                     "Episode frequency at which the agents learn.")
flags.DEFINE_integer("save_every", 5000,
                     "Episode frequency at which the agents save the policies.")
flags.DEFINE_list("output_channels", [
    2, 4, 8, 16, 32
], "")
flags.DEFINE_list("hidden_layers_sizes", [
    32, 64, 14
], "Number of hidden units in the net.")
flags.DEFINE_integer("replay_buffer_capacity", int(5e4),
                     "Size of the replay buffer.")
flags.DEFINE_integer("reservoir_buffer_capacity", int(2e6),
                     "Size of the reservoir buffer.")



def fmt_hyperparameters():
    fmt = ""
    for i in FLAGS.output_channels:
        fmt += '_{}'.format(i)
    fmt += '**'
    for i in FLAGS.hidden_layers_sizes:
        fmt += '_{}'.format(i)
    return fmt


def init_env():
    begin = time.time()
    env = Go(flatten_board_state=False)
    info_state_size = env.state_size
    print("info_state_size:", info_state_size)
    num_actions = env.action_size
    num_layer = len(FLAGS.output_channels)
    kernel_shapes = [3 for _ in range(num_layer)]
    strides = [1 for _ in range(num_layer)]
    paddings = ["SAME" for _ in range(num_layer - 1)]
    paddings.append("VALID")

    parameters = [FLAGS.output_channels, kernel_shapes, strides, paddings]

    hidden_layers_sizes = [int(l) for l in FLAGS.hidden_layers_sizes]


    kwargs = {
        "pi_learning_rate": 3e-4,
        "critic_learning_rate": 1e-3,
        "batch_size": 128,
        "entropy_cost": 0.5,
        "max_global_gradient_norm": 20,
    }
    ret = [0]
    max_len = 2000

    return env, info_state_size, num_actions, begin, parameters, hidden_layers_sizes, kwargs, ret, max_len



def init_agents(sess, info_state_size, num_actions, parameters, hidden_layers_sizes, rival_path, **kwargs):

    with tf.name_scope("rival"):
        rival = PolicyGradient(sess, 1, info_state_size ** 0.5, num_actions,
                               parameters, hidden_layers_sizes, **kwargs)
        # sess.run(tf.local_variables_initializer())
    with tf.name_scope("self"):
        self_ = PolicyGradient(sess, 0, info_state_size ** 0.5, num_actions,
                               parameters, hidden_layers_sizes, **kwargs)
        sess.run(tf.local_variables_initializer())
        self_.restore(rival_path)

    agents = [self_, rival]
    sess.run(tf.global_variables_initializer())
    rival.restore(rival_path)

    restore_agent_op = tf.group([
        tf.assign(self_v, rival_v)
        for (self_v, rival_v) in zip(self_.variable_list, rival.variable_list)
    ])
    sess.run(restore_agent_op)

    logging.info("Load self and rival agents ok!!")

    return agents


def prt_logs(ep, agents, ret, begin):
    losses = agents[0].loss
    logging.info("Episodes: {}: Losses: {}, Rewards: {}".format(ep + 1, losses, np.mean(ret)))

    alg_tag = "a2c_vs_rnd"

    with open('current_logs/log_{}_{}'.format(os.environ.get('BOARD_SIZE'), alg_tag + fmt_hyperparameters()),
              'a+') as log_file:
        log_file.writelines("{}, {}\n".format(ep + 1, np.mean(ret)))


def save_model(ep, agents):
    alg_tag = "current_models/A2C"

    if not os.path.exists(alg_tag + fmt_hyperparameters()):
        os.mkdir(alg_tag + fmt_hyperparameters())
    agents[0].save(checkpoint_root=alg_tag + fmt_hyperparameters(), checkpoint_name='{}'.format(ep + 1))

    print("Model Saved!")


def restore_model(agents, path=None):
    alg_tag = "current_models/A2C"
    try:

        if path:
            agents[0].restore(path)
            idex = path.split("/")[-1]
        else:
            idex = get_max_idx(alg_tag + fmt_hyperparameters())
            path = os.path.join(alg_tag + fmt_hyperparameters(), str(idex))
            agents[0].restore(path)

        logging.info("Agent model restored at {}".format(path))

    except:
        print(sys.exc_info())
        logging.info("No saved Model!!")
        idex = 0

    return int(idex)


def train(agents, env, ret, max_len, begin):
    logging.info("Train on " + fmt_hyperparameters())
    global_ep = restore_model(agents)
    try:
        for ep in range(FLAGS.num_train_episodes):
            if (ep + 1) % FLAGS.eval_every == 0:
                prt_logs(global_ep + ep, agents, ret, begin)

            if (ep + 1) % FLAGS.save_every == 0:
                save_model(global_ep + ep, agents)

            time_step = env.reset()  # a go.Position object

            while not time_step.last():
                player_id = time_step.observations["current_player"]
                agent_output = agents[player_id].step(time_step, is_rival=(player_id == 0))
                action_list = agent_output.action
                print(player_id)
                print(action_list)
                time_step = env.step(action_list)


            for agent in agents:
                agent.step(time_step)

            if len(ret) < max_len:

                ret.append(time_step.rewards[0])

            else:

                ret[ep % max_len] = time_step.rewards[0]

    except KeyboardInterrupt:

        save_model(global_ep + ep, agents)


def evaluate(agents, env):
    global_ep = restore_model(agents, "../saved_model/important/policy_final")

    ret = []

    for ep in range(FLAGS.num_eval):
        time_step = env.reset()
        while not time_step.last():
            player_id = time_step.observations["current_player"]
            if player_id == 0:
                agent_output = agents[player_id].step(time_step, is_evaluation=True)
            else:
                agent_output = agents[player_id].step(time_step)
            action_list = agent_output.action
            time_step = env.step(action_list)

        # Episode is over, step all agents with final info state.
        # for agent in agents:
        agents[0].step(time_step, is_evaluation=True)
        agents[1].step(time_step)
        ret.append(time_step.rewards[0])

    return ret


def stat(ret, begin):
    print(np.mean(ret))

    print('Time elapsed:', time.time() - begin)


def main(unused_argv):
    env, info_state_size, num_actions, begin,parameters, hidden_layers_sizes, kwargs, ret, max_len = init_env()

    with tf.Session() as sess:
        rival_path = "../saved_model/important" + fmt_hyperparameters()

        rival_model = os.path.join(rival_path, str(get_max_idx(rival_path)))
        agents = init_agents(sess, info_state_size, num_actions, parameters, hidden_layers_sizes, rival_model,
                             **kwargs)

        train(agents, env, ret, max_len, begin)

        ret = evaluate(agents, env)

        stat(ret, begin)


if __name__ == '__main__':
    app.run(main)
