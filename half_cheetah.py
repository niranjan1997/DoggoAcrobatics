#### PUT THIS FILE IN gym/gym/envs/mujoco/ !!! #######


import numpy as np
from gym import utils
from gym.envs.mujoco import mujoco_env

class HalfCheetahEnv(mujoco_env.MujocoEnv, utils.EzPickle):
    def __init__(self):
        self.paction = np.zeros((4,))
        mujoco_env.MujocoEnv.__init__(self, 'half_cheetah.xml', 1)
        # mujoco_env.MujocoEnv.__init__(self, 'half_cheetah.xml', 5)
        utils.EzPickle.__init__(self)

    def step(self, action):
        prev_pos = (self.sim.data.qpos).copy()
        self.do_simulation(action, self.frame_skip)
        new_pos = (self.sim.data.qpos).copy()

        ob = self._get_obs()

        reward = [] # Type: List[float]

        for i in range(self.sim.data.ncon):
            contact = self.sim.data.contact[i]
            c1 = self.sim.model.geom_id2name(contact.geom1)
            c2 = self.sim.model.geom_id2name(contact.geom2)
            # print('contact', i)
            # print('dist', contact.dist)
            # print('geom1', contact.geom1, self.sim.model.geom_id2name(contact.geom1))
            # print('geom2', contact.geom2, self.sim.model.geom_id2name(contact.geom2))
            if c2 == 'torso':
                reward.append(-100)

        reward.append( - 1e-6 * np.dot(action,action) / self.dt)

        # Reward for changing the angle (make it spin)
        reward.append(0.0 * (new_pos[2] - prev_pos[2])/self.dt)

        # X velocity, so it moves forward
        reward.append(10.0 * (new_pos[0] - prev_pos[0])/self.dt) 

        done = False

        self.paction = action
        rewards = {}
        for idx, val in enumerate(reward):
            rewards[idx] = val
        return ob, sum(reward), done, rewards

    def _get_obs(self):
        # return np.concatenate([
        #     self.sim.data.qpos.flat[1:3],
        #     self.sim.data.qvel.flat[0:3],
        # ])
        return np.concatenate([
            self.sim.data.qpos.flat[1:],
            self.sim.data.qvel.flat,
        ])

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(low=-.1, high=.1, size=self.model.nq)
        qvel = self.init_qvel + self.np_random.randn(self.model.nv) * .1
        self.paction = 0
        self.set_state(qpos, qvel)
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = self.model.stat.extent * 0.5
