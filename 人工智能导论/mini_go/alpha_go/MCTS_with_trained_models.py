import sys
sys.path.append("../")
import warnings
from absl import logging, flags, app
from environment.GoEnv import Go
import time, os
import numpy as np
import tensorflow as tf
from algorithms.policy_gradient import PolicyGradient
from agent.agent import MCTSAgent

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
flags.DEFINE_bool("use_dqn", False, "use dqn or not. If set to false, use a2c")
flags.DEFINE_float("lr", 2e-4, "lr")
flags.DEFINE_integer("pd", 10, "playout_depth")
flags.DEFINE_integer("np", 100, "n_playout")


def init_env():
    begin = time.time()
    env = Go(flatten_board_state=False)
    info_state_size = env.state_size
    print(info_state_size)
    num_actions = env.action_size
    num_layer = len(FLAGS.output_channels)
    kernel_shapes = [3 for _ in range(num_layer)]
    strides = [1 for _ in range(num_layer)]
    paddings = ["SAME" for _ in range(num_layer - 1)]
    paddings.append("VALID")

    parameters = [FLAGS.output_channels, kernel_shapes, strides, paddings]

    hidden_layers_sizes = [int(l) for l in FLAGS.hidden_layers_sizes]

    dqn_kwargs = {
        "hidden_layers_sizes": [128, 128],
        "replay_buffer_capacity": FLAGS.replay_buffer_capacity,
        "epsilon_decay_duration": int(0.6 * FLAGS.num_train_episodes),
        "epsilon_start": 0.8,
        "epsilon_end": 0.001,
        "learning_rate": FLAGS.lr,
        "learn_every": FLAGS.learn_every,
        "batch_size": 256,
        "max_global_gradient_norm": 10,
    }

    a2c_kwargs = {
        "hidden_layers_sizes": hidden_layers_sizes,
        "parameters": parameters,
        "pi_learning_rate": 3e-4,
        "critic_learning_rate": 1e-3,
        "batch_size": 128,
        "entropy_cost": 0.5,
        "max_global_gradient_norm": 20,
    }

    return env, info_state_size, num_actions, begin,dqn_kwargs, a2c_kwargs


def init_agents(sess, info_state_size, num_actions, dqn_kwargs, a2c_kwargs):
    policy_module = PolicyGradient(sess, 0, info_state_size ** 0.5, num_actions, **a2c_kwargs)
    rollout_module = PolicyGradient(sess, 0, info_state_size ** 0.5, num_actions, **a2c_kwargs)
    sess.run(tf.global_variables_initializer())

    policy_module.restore("../saved_model/important/policy_final")
    restore_agent_op = tf.group([
        tf.assign(rollout_v, policy_v)
        for (rollout_v, policy_v) in zip(rollout_module.variable_list, policy_module.variable_list)
    ])
    sess.run(restore_agent_op)
    agents = [MCTSAgent(policy_module, rollout_module, playout_depth=FLAGS.pd, n_playout=FLAGS.np),
              MCTSAgent(None, None)]

    print("MCTS INIT OK!!")

    return agents


def evaluate(agents, env):
    ret = []

    for ep in range(FLAGS.num_eval):
        time_step = env.reset()
        while not time_step.last():
            player_id = time_step.observations["current_player"]
            if player_id == 0:
                agent_output = agents[player_id].step(time_step, env)
                action_list = agent_output
            else:
                agent_output = agents[player_id].step(time_step, env)
                action_list = agent_output
            time_step = env.step(action_list)
        print("α-go : random  ", time_step.rewards)
        ret.append(time_step.rewards[0])

    return ret


def stat(ret, begin):
    print(np.mean(ret))

    print('Time elapsed:', time.time() - begin)


def main(unused_argv):
    warnings.filterwarnings("ignore")
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    env, info_state_size, num_actions, begin, dqn_kwargs, a2c_kwargs = init_env()

    with tf.Session() as sess:
        agents = init_agents(sess, info_state_size, num_actions, dqn_kwargs, a2c_kwargs)

        ret = evaluate(agents, env)

        stat(ret, begin)


if __name__ == '__main__':
    app.run(main)
