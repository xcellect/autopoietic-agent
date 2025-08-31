# autopoietic_learner.py
import pybullet as p
import numpy as np
import torch
import torch.nn as nn
import time

class AutopoieticAgent:
    """
    Self-Organizing Embodied Learner with Energy Constraints
    
    Key principle: Every computation costs energy (Landauer's principle)
    Agent must balance survival (finding food) vs intelligence (learning)
    """
    
    def __init__(self, gui=False, debug=False):
        # Physics setup
        if gui:
            self.client = p.connect(p.GUI)
        else:
            self.client = p.connect(p.DIRECT)
        p.setGravity(0, 0, -9.8)
        
        # Debug settings
        self.debug = debug
        self.debug_lines = []  # Store debug line IDs for cleanup
        
        # Energy system (the key innovation)
        self.energy = 100.0
        self.max_energy = 150.0
        self.energy_decay = 0.1  # Natural energy loss per timestep
        self.landauer_cost = 0.01  # Cost per computation
        self.sensing_cost = 0.02
        self.acting_cost = 0.03
        self.learning_cost = 0.05
        
        # Learning threshold - only learn when energy is sufficient
        self.learning_threshold = 50.0
        
        # Simple neural controller
        self.brain = nn.Sequential(
            nn.Linear(8, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 4)  # [forward, backward, left, right]
        )
        self.optimizer = torch.optim.Adam(self.brain.parameters(), lr=0.001)
        
        # Initialize with slight bias toward exploration/movement
        with torch.no_grad():
            # Add small bias to output layer to encourage movement
            self.brain[-1].bias.data += torch.tensor([0.1, 0.1, 0.1, 0.1])  # Small positive bias for all actions
        
        # Exploration parameters - more aggressive
        self.epsilon = 0.5  # Start with very high exploration
        self.epsilon_decay = 0.998  # Slower decay to maintain exploration longer
        self.epsilon_min = 0.1  # Higher minimum exploration
        
        # Create environment
        self.setup_environment()
        
        # History tracking
        self.history = []
        self.step_count = 0
        
    def setup_environment(self):
        """Create robot and food sources"""
        # Ground plane
        p.createMultiBody(
            baseCollisionShapeIndex=p.createCollisionShape(p.GEOM_PLANE),
            basePosition=[0, 0, 0]
        )
        
        # Robot body - simple sphere that can roll
        self.robot_id = p.createMultiBody(
            baseMass=1.0,
            baseCollisionShapeIndex=p.createCollisionShape(p.GEOM_SPHERE, radius=0.3),
            baseVisualShapeIndex=p.createVisualShape(p.GEOM_SPHERE, radius=0.3, rgbaColor=[0, 0, 1, 1]),
            basePosition=[0, 0, 0.5]
        )
        
        # Food sources - increase density for better learning
        self.food_positions = []
        self.spawn_food(n=16)  # More food sources for better finding chances
        
    def spawn_food(self, n=12):
        """Create energy sources in environment"""
        for i in range(n):
            # Smaller environment for better food density
            pos = [
                np.random.uniform(-5, 5), 
                np.random.uniform(-5, 5), 
                0.3
            ]
            food = p.createMultiBody(
                baseMass=0.1,
                baseCollisionShapeIndex=p.createCollisionShape(p.GEOM_SPHERE, radius=0.2),
                baseVisualShapeIndex=p.createVisualShape(
                    p.GEOM_SPHERE, 
                    radius=0.2, 
                    rgbaColor=[0, 1, 0, 1]
                ),
                basePosition=pos
            )
            self.food_positions.append(food)
    
    def sense(self):
        """Get observations - costs energy!"""
        self.energy -= self.sensing_cost
        
        # Get robot state
        robot_pos, robot_orn = p.getBasePositionAndOrientation(self.robot_id)
        robot_vel, _ = p.getBaseVelocity(self.robot_id)
        
        # Find nearest food
        min_dist = float('inf')
        nearest_food_pos = [0, 0, 0]
        
        for food_id in self.food_positions:
            try:
                food_pos, _ = p.getBasePositionAndOrientation(food_id)
                dist = np.linalg.norm(np.array(robot_pos[:2]) - np.array(food_pos[:2]))
                if dist < min_dist:
                    min_dist = dist
                    nearest_food_pos = food_pos
            except:
                continue  # Food might have been removed
        
        # Construct observation vector
        obs = [
            robot_pos[0],  # robot x
            robot_pos[1],  # robot y  
            robot_vel[0],  # robot vel x
            robot_vel[1],  # robot vel y
            nearest_food_pos[0] - robot_pos[0],  # relative food x
            nearest_food_pos[1] - robot_pos[1],  # relative food y
            min_dist,  # distance to nearest food
            self.energy / self.max_energy  # normalized energy level
        ]
        
        return torch.tensor(obs, dtype=torch.float32)
    
    def act(self, obs):
        """Take action based on neural network - costs energy!"""
        self.energy -= self.acting_cost
        
        # Neural network decision (keep gradients for learning)
        action_logits = self.brain(obs)
        action_probs = torch.softmax(action_logits, dim=0)
        
        # Convert to forces - even stronger movement for better navigation
        force_magnitude = 40.0
        forces = {
            0: [force_magnitude, 0, 0],   # forward
            1: [-force_magnitude, 0, 0],  # backward  
            2: [0, force_magnitude, 0],   # left
            3: [0, -force_magnitude, 0]   # right
        }
        
        # Select action with food-seeking heuristic when close
        with torch.no_grad():
            # Extract relative food position from observation
            rel_food_x = obs[4].item()
            rel_food_y = obs[5].item()
            distance_to_food = obs[6].item()
            
            # Use heuristic when close to food (within 4 units)  
            if distance_to_food < 4.0 and np.random.random() < 0.5:  # 50% chance to use heuristic when close
                # Simple heuristic: move toward food
                if abs(rel_food_x) > abs(rel_food_y):
                    action_idx = 0 if rel_food_x > 0 else 1  # forward/backward
                else:
                    action_idx = 2 if rel_food_y > 0 else 3  # left/right
            elif np.random.random() < self.epsilon:
                action_idx = np.random.randint(4)
            else:
                action_idx = torch.argmax(action_probs).item()
        
        # Decay exploration over time
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
        
        # Apply force
        p.applyExternalForce(
            self.robot_id, 
            -1, 
            forces[action_idx], 
            [0, 0, 0], 
            p.WORLD_FRAME
        )
        
        # Step simulation
        p.stepSimulation()
        
        return action_logits, action_idx
    
    def check_food_consumption(self):
        """Check if robot is near food and consume it"""
        robot_pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        
        for i, food_id in enumerate(self.food_positions):
            try:
                food_pos, _ = p.getBasePositionAndOrientation(food_id)
                distance = np.linalg.norm(np.array(robot_pos[:2]) - np.array(food_pos[:2]))
                
                if distance < 0.8:  # Larger consumption radius for easier eating
                    # Gain energy
                    energy_gain = np.random.uniform(15, 25)
                    self.energy = min(self.energy + energy_gain, self.max_energy)
                    
                    # Respawn food in new location (smaller area)
                    new_pos = [
                        np.random.uniform(-5, 5),
                        np.random.uniform(-5, 5), 
                        0.3
                    ]
                    p.resetBasePositionAndOrientation(food_id, new_pos, [0, 0, 0, 1])
                    return True
                    
            except:
                continue
                
        return False
    
    def calculate_shaped_reward(self, obs, ate_food):
        """Calculate reward with distance-based shaping"""
        if ate_food:
            return 50.0  # Very large reward for eating
        
        # Extract distance to nearest food from observation
        min_dist = obs[6].item()  # Distance is at index 6
        
        # Stronger distance-based reward shaping
        max_dist = 12.0  # Maximum possible distance in 12x12 environment
        distance_reward = (max_dist - min_dist) / max_dist * 1.0  # Scale to 0-1.0 (stronger)
        
        # Smaller penalty for existing
        existence_penalty = -0.005
        
        return distance_reward + existence_penalty
    
    def debug_visualize(self, robot_pos, nearest_food_pos):
        """Add debug visualization lines"""
        if not self.debug:
            return
            
        # Clear previous debug lines
        for line_id in self.debug_lines:
            try:
                p.removeUserDebugItem(line_id)
            except:
                pass
        self.debug_lines.clear()
        
        # Draw line to nearest food
        line_id = p.addUserDebugLine(
            robot_pos, nearest_food_pos, 
            lineColorRGB=[1, 0, 0], lineWidth=2
        )
        self.debug_lines.append(line_id)
        
        # Draw robot trajectory (last 10 positions)
        if len(self.history) > 1:
            recent_positions = [h['position'] for h in self.history[-10:]]
            for i in range(len(recent_positions) - 1):
                line_id = p.addUserDebugLine(
                    recent_positions[i], recent_positions[i+1],
                    lineColorRGB=[0, 0, 1], lineWidth=1
                )
                self.debug_lines.append(line_id)
    
    def learn(self, obs, action_logits, action_idx, reward):
        """Update neural network - costs energy!"""
        if self.energy < self.learning_threshold:
            return  # Can't afford to learn when energy is low
            
        self.energy -= self.learning_cost
        
        # Policy gradient learning: REINFORCE algorithm
        # Get action probabilities
        action_probs = torch.softmax(action_logits, dim=0)
        
        # Calculate log probability of selected action
        log_prob = torch.log(action_probs[action_idx] + 1e-8)  # Add small epsilon for numerical stability
        
        # Policy gradient loss: -log_prob * reward (negative because we want to maximize reward)
        loss = -log_prob * reward
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def live_and_learn(self, max_steps=2000):
        """Main autopoietic loop: survive or die"""
        print("Starting autopoietic agent simulation...")
        
        for step in range(max_steps):
            self.step_count = step
            
            # Natural energy decay
            self.energy -= self.energy_decay
            
            # Death condition
            if self.energy <= 0:
                print(f"Agent died at step {step} due to energy depletion")
                break
            
            # Sense-act-eat cycle
            obs = self.sense()
            action_logits, action_idx = self.act(obs)
            ate_food = self.check_food_consumption()
            
            # Debug visualization
            if self.debug and step % 10 == 0:  # Every 10 steps to avoid clutter
                robot_pos, _ = p.getBasePositionAndOrientation(self.robot_id)
                # Find nearest food for visualization
                nearest_food_pos = [obs[4].item() + robot_pos[0], obs[5].item() + robot_pos[1], 0.3]
                self.debug_visualize(robot_pos, nearest_food_pos)
            
            # Calculate reward with distance-based shaping
            reward = self.calculate_shaped_reward(obs, ate_food)
            
            # Learn from all experiences if we have sufficient energy
            can_learn = self.energy > self.learning_threshold
            if can_learn:  # Learn from all experiences, not just eating
                self.learn(obs, action_logits, action_idx, reward)
            
            # Record state
            self.history.append({
                'step': step,
                'energy': self.energy,
                'ate': ate_food,
                'can_learn': can_learn,
                'position': p.getBasePositionAndOrientation(self.robot_id)[0],
                'total_computation_cost': self.sensing_cost + self.acting_cost + (self.learning_cost if can_learn else 0)
            })
            
            # Progress updates
            if step % 100 == 0:
                avg_energy = np.mean([h['energy'] for h in self.history[-100:]])
                food_eaten = sum([h['ate'] for h in self.history[-100:]])
                print(f"Step {step}: Energy={self.energy:.1f}, Avg Energy={avg_energy:.1f}, Food eaten={food_eaten}")
        
        print(f"Simulation completed. Agent survived {len(self.history)} steps")
        return self.history
    
    def get_survival_stats(self):
        """Calculate key survival metrics"""
        if not self.history:
            return {}
            
        total_food = sum([h['ate'] for h in self.history])
        learning_episodes = sum([h['can_learn'] for h in self.history])
        avg_energy = np.mean([h['energy'] for h in self.history])
        
        return {
            'survival_time': len(self.history),
            'total_food_consumed': total_food,
            'learning_episodes': learning_episodes,
            'average_energy': avg_energy,
            'learning_ratio': learning_episodes / len(self.history) if self.history else 0,
            'feeding_efficiency': total_food / len(self.history) if self.history else 0
        }
    
    def cleanup(self):
        """Clean up PyBullet simulation"""
        p.disconnect(self.client)

if __name__ == "__main__":
    # Quick test
    agent = AutopoieticAgent(gui=False)
    history = agent.live_and_learn(max_steps=1000)
    stats = agent.get_survival_stats()
    
    print("\nFinal Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    agent.cleanup()