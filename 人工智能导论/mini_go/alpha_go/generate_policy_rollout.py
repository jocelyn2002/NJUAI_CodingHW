import sys
sys.path.append("../")
from absl import logging, flags, app
from environment.GoEnv import Go
import time, os
import numpy as np
import tensorflow as tf
from algorithms.dqn import DQN
import agent.agent as ag

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

max_len = 2000
rollout_hidden_layers_sizes = [32, 32]  # 用于rollout,蒙特卡洛树
policy_hidden_layers_sizes = [32, 64, 14]  # 用于之后的Q-learning


def init_env():
    begin = time.time()
    env = Go(flatten_board_state=False)
    info_state_size = env.state_size
    print(info_state_size)
    num_actions = env.action_size
    num_cnn_layer = len(FLAGS.output_channels)
    kernel_shapes = [3 for _ in range(num_cnn_layer)]
    strides = [1 for _ in range(num_cnn_layer)]
    paddings = ["SAME" for _ in range(num_cnn_layer - 1)]
    paddings.append("VALID")

    cnn_parameters = [FLAGS.output_channels, kernel_shapes, strides, paddings]

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
        "cnn_parameters": cnn_parameters,
        "pi_learning_rate": 3e-4,
        "critic_learning_rate": 1e-3,
        "batch_size": 128,
        "entropy_cost": 0.5,
        "max_global_gradient_norm": 20,
    }

    return env, info_state_size, num_actions, begin,dqn_kwargs, a2c_kwargs

def generate_rollout_and_policy():
    with tf.Session() as sess:
        # 加载全局参数
        env, info_state_size, num_actions, begin, dqn_kwargs, a2c_kwargs = init_env()
        # 训练rollout网络
        ret = [0]

        agents = [DQN(sess, 0, info_state_size,
                      num_actions, rollout_hidden_layers_sizes, **dqn_kwargs), ag.RandomAgent(1)]
        sess.run(tf.global_variables_initializer())

        # train the agent
        for ep in range(FLAGS.num_train_episodes):
            if (ep + 1) % FLAGS.eval_every == 0:
                losses = agents[0].loss
                logging.info("Episodes: {}: Losses: {}, Rewards: {}".format(ep + 1, losses, np.mean(ret)))
                with open('log_{}_{}'.format(os.environ.get('BOARD_SIZE'), begin), 'a+') as log_file:
                    log_file.writelines("{}, {}\n".format(ep + 1, np.mean(ret)))
            if (ep + 1) % FLAGS.save_every == 0:
                if not os.path.exists("saved_model"):
                    os.mkdir('saved_model')
                agents[0].save(checkpoint_root='saved_model', checkpoint_name='rollout{}'.format(ep + 1))
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

        # evaluated the trained agent
        agents[0].restore("saved_model/rollout10000")
        agents[0].save(checkpoint_root='saved_model/important', checkpoint_name='rollout_final')
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
        print('rollout reward:', np.mean(ret))
        return_value1 = agents[0]
        # 训练policy初始网络
        ret = [0]
        agents = [DQN(sess, 0, info_state_size,
                      num_actions, policy_hidden_layers_sizes, **dqn_kwargs), ag.RandomAgent(1)]
        sess.run(tf.global_variables_initializer())
        # train the agent
        for ep in range(FLAGS.num_train_episodes):
            if (ep + 1) % FLAGS.eval_every == 0:
                losses = agents[0].loss
                logging.info("Episodes: {}: Losses: {}, Rewards: {}".format(ep + 1, losses, np.mean(ret)))
                with open('log_{}_{}'.format(os.environ.get('BOARD_SIZE'), begin), 'a+') as log_file:
                    log_file.writelines("{}, {}\n".format(ep + 1, np.mean(ret)))
            if (ep + 1) % FLAGS.save_every == 0:
                if not os.path.exists("saved_model"):
                    os.mkdir('saved_model')
                agents[0].save(checkpoint_root='saved_model', checkpoint_name='policy_initial{}'.format(ep + 1))
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

        # evaluated the trained agent
        agents[0].restore("./saved_model/policy_initial10000")
        agents[0].save(checkpoint_root='./saved_model/important', checkpoint_name='policy_final')
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
        print('policy reward:', np.mean(ret))


def main(unused_argv):
    generate_rollout_and_policy()


if __name__ == '__main__':
    app.run(main)
