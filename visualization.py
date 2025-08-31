# visualization.py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import seaborn as sns
import os

def visualize_autopoiesis(history, save_path="results/autopoiesis_analysis.png"):
    """
    Comprehensive visualization of autopoietic agent behavior
    """
    if not history:
        print("No history data to visualize")
        return None
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Autopoietic Agent Analysis: Energy-Constrained Learning', fontsize=16)
    
    # Extract data
    steps = [h['step'] for h in history]
    energies = [h['energy'] for h in history]
    ate_events = [h['ate'] for h in history]
    learning_events = [h['can_learn'] for h in history]
    positions = [h['position'] for h in history]
    
    # 1. Energy over time
    axes[0, 0].plot(steps, energies, 'b-', alpha=0.8, linewidth=2)
    axes[0, 0].axhline(y=50, color='r', linestyle='--', alpha=0.7, label='Learning Threshold')
    axes[0, 0].axhline(y=0, color='k', linestyle='-', alpha=0.7, label='Death')
    
    # Highlight feeding events
    feed_times = [s for s, ate in zip(steps, ate_events) if ate]
    feed_energies = [energies[i] for i, ate in enumerate(ate_events) if ate]
    axes[0, 0].scatter(feed_times, feed_energies, c='green', s=30, alpha=0.8, label='Fed')
    
    axes[0, 0].set_xlabel('Time Step')
    axes[0, 0].set_ylabel('Energy Level')
    axes[0, 0].set_title('Energy Evolution')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Learning vs Survival phases
    survival_only = [1 if not learn else 0 for learn in learning_events]
    learning_active = [1 if learn else 0 for learn in learning_events]
    
    axes[0, 1].fill_between(steps, 0, survival_only, alpha=0.6, color='red', label='Survival Mode')
    axes[0, 1].fill_between(steps, survival_only, np.array(survival_only) + np.array(learning_active), 
                           alpha=0.6, color='blue', label='Learning Mode')
    axes[0, 1].set_xlabel('Time Step')
    axes[0, 1].set_ylabel('Agent State')
    axes[0, 1].set_title('Learning vs Survival Modes')
    axes[0, 1].legend()
    axes[0, 1].set_ylim(0, 1.2)
    
    # 3. Spatial trajectory
    x_pos = [pos[0] for pos in positions]
    y_pos = [pos[1] for pos in positions]
    
    # Color trajectory by energy level
    scatter = axes[0, 2].scatter(x_pos, y_pos, c=energies, cmap='coolwarm', s=10, alpha=0.7)
    axes[0, 2].set_xlabel('X Position')
    axes[0, 2].set_ylabel('Y Position')
    axes[0, 2].set_title('Movement Trajectory (colored by energy)')
    plt.colorbar(scatter, ax=axes[0, 2], label='Energy Level')
    
    # 4. Feeding pattern analysis
    if feed_times:
        feed_intervals = np.diff(feed_times)
        axes[1, 0].hist(feed_intervals, bins=20, alpha=0.7, color='green', edgecolor='black')
        axes[1, 0].set_xlabel('Time Between Meals')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Feeding Pattern Distribution')
        axes[1, 0].axvline(np.mean(feed_intervals), color='red', linestyle='--', 
                          label=f'Mean: {np.mean(feed_intervals):.1f}')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Energy efficiency over time (rolling window)
    window_size = 50
    if len(history) >= window_size:
        efficiency = []
        for i in range(window_size, len(history)):
            window_data = history[i-window_size:i]
            food_consumed = sum([h['ate'] for h in window_data])
            energy_spent = sum([h['total_computation_cost'] for h in window_data])
            efficiency.append(food_consumed / max(energy_spent, 0.001))
        
        axes[1, 1].plot(range(window_size, len(history)), efficiency, 'purple', linewidth=2)
        axes[1, 1].set_xlabel('Time Step')
        axes[1, 1].set_ylabel('Feeding Efficiency')
        axes[1, 1].set_title(f'Energy Efficiency (rolling window={window_size})')
        axes[1, 1].grid(True, alpha=0.3)
    
    # 6. Summary statistics
    total_food = sum(ate_events)
    learning_ratio = sum(learning_events) / len(learning_events) if learning_events else 0
    avg_energy = np.mean(energies)
    survival_time = len(history)
    
    stats_text = f"""Survival Statistics:
    
Survival Time: {survival_time} steps
Total Food Consumed: {total_food}
Learning Ratio: {learning_ratio:.2%}
Average Energy: {avg_energy:.1f}
Final Energy: {energies[-1]:.1f}

Efficiency Metrics:
Food/Time: {total_food/survival_time:.3f}
Learning/Time: {learning_ratio:.3f}
    """
    
    axes[1, 2].text(0.05, 0.95, stats_text, transform=axes[1, 2].transAxes, 
                    fontsize=10, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    axes[1, 2].set_xlim(0, 1)
    axes[1, 2].set_ylim(0, 1)
    axes[1, 2].axis('off')
    axes[1, 2].set_title('Summary Statistics')
    
    plt.tight_layout()
    
    # Create results directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {save_path}")
    
    return fig

def compare_energy_scenarios(agent_class, scenarios, max_steps=1000):
    """
    Compare agent performance under different energy constraints
    """
    results = {}
    
    for scenario_name, params in scenarios.items():
        print(f"Running scenario: {scenario_name}")
        
        agent = agent_class(gui=False)
        
        # Modify agent parameters based on scenario
        for param, value in params.items():
            setattr(agent, param, value)
        
        history = agent.live_and_learn(max_steps=max_steps)
        results[scenario_name] = {
            'history': history,
            'stats': agent.get_survival_stats()
        }
        agent.cleanup()
    
    return results

def plot_scenario_comparison(results, save_path="results/scenario_comparison.png"):
    """
    Visualize comparison between different energy scenarios
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Autopoietic Agent: Energy Constraint Comparison', fontsize=14)
    
    scenarios = list(results.keys())
    colors = plt.cm.Set3(np.linspace(0, 1, len(scenarios)))
    
    # 1. Survival time comparison
    survival_times = [results[s]['stats']['survival_time'] for s in scenarios]
    bars1 = axes[0, 0].bar(scenarios, survival_times, color=colors, alpha=0.8)
    axes[0, 0].set_ylabel('Survival Time (steps)')
    axes[0, 0].set_title('Survival Duration by Scenario')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars1, survival_times):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                       f'{int(value)}', ha='center', va='bottom')
    
    # 2. Learning efficiency
    learning_ratios = [results[s]['stats']['learning_ratio'] for s in scenarios]
    bars2 = axes[0, 1].bar(scenarios, learning_ratios, color=colors, alpha=0.8)
    axes[0, 1].set_ylabel('Learning Ratio')
    axes[0, 1].set_title('Learning Time Percentage')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    for bar, value in zip(bars2, learning_ratios):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.2%}', ha='center', va='bottom')
    
    # 3. Energy trajectories over time
    for i, (scenario, color) in enumerate(zip(scenarios, colors)):
        history = results[scenario]['history']
        energies = [h['energy'] for h in history]
        steps = [h['step'] for h in history]
        axes[1, 0].plot(steps, energies, color=color, label=scenario, linewidth=2, alpha=0.8)
    
    axes[1, 0].axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Learning Threshold')
    axes[1, 0].set_xlabel('Time Step')
    axes[1, 0].set_ylabel('Energy Level')
    axes[1, 0].set_title('Energy Evolution Comparison')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Efficiency metrics scatter
    feeding_efficiency = [results[s]['stats']['feeding_efficiency'] for s in scenarios]
    axes[1, 1].scatter(learning_ratios, feeding_efficiency, c=colors, s=100, alpha=0.8)
    
    # Add scenario labels
    for i, scenario in enumerate(scenarios):
        axes[1, 1].annotate(scenario, (learning_ratios[i], feeding_efficiency[i]),
                          xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    axes[1, 1].set_xlabel('Learning Ratio')
    axes[1, 1].set_ylabel('Feeding Efficiency')
    axes[1, 1].set_title('Learning vs Feeding Efficiency')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create results directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Scenario comparison saved to {save_path}")
    
    return fig

def animate_agent_trajectory(history, save_path="agent_animation.gif"):
    """
    Create animated visualization of agent movement and energy
    """
    if len(history) < 10:
        print("Not enough data for animation")
        return None
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Extract data
    positions = [h['position'] for h in history]
    energies = [h['energy'] for h in history]
    steps = [h['step'] for h in history]
    
    x_pos = [pos[0] for pos in positions]
    y_pos = [pos[1] for pos in positions]
    
    # Set up plots
    ax1.set_xlim(min(x_pos)-1, max(x_pos)+1)
    ax1.set_ylim(min(y_pos)-1, max(y_pos)+1)
    ax1.set_xlabel('X Position')
    ax1.set_ylabel('Y Position')
    ax1.set_title('Agent Movement')
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlim(0, max(steps))
    ax2.set_ylim(0, max(energies)+10)
    ax2.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Learning Threshold')
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Energy Level')
    ax2.set_title('Energy Evolution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Animation objects
    trail_line, = ax1.plot([], [], 'b-', alpha=0.5, linewidth=1)
    agent_dot, = ax1.plot([], [], 'ro', markersize=8)
    energy_line, = ax2.plot([], [], 'g-', linewidth=2)
    
    def animate(frame):
        # Trail (last 50 positions)
        start_idx = max(0, frame-50)
        trail_line.set_data(x_pos[start_idx:frame+1], y_pos[start_idx:frame+1])
        
        # Current position
        agent_dot.set_data([x_pos[frame]], [y_pos[frame]])
        
        # Energy trajectory
        energy_line.set_data(steps[:frame+1], energies[:frame+1])
        
        return trail_line, agent_dot, energy_line
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=len(history), 
                        interval=50, blit=True, repeat=True)
    
    # Save as GIF
    anim.save(save_path, writer='pillow', fps=20)
    print(f"Animation saved to {save_path}")
    
    plt.close(fig)
    return anim

if __name__ == "__main__":
    # Test visualization with dummy data
    dummy_history = [
        {
            'step': i,
            'energy': 100 - i*0.1 + np.random.normal(0, 2),
            'ate': i % 20 == 0,
            'can_learn': (100 - i*0.1) > 50,
            'position': (np.random.normal(0, 2), np.random.normal(0, 2), 0.5),
            'total_computation_cost': 0.06
        }
        for i in range(500)
    ]
    
    visualize_autopoiesis(dummy_history, "test_visualization.png")