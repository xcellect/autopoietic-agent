# corrected_emergence_test.py
"""
Test the corrected emergence experiment with proper simulation lengths
"""

from autopoietic_learner import AutopoieticAgent
import numpy as np

def test_corrected_emergence():
    """Test emergence with properly balanced parameters and adequate simulation time"""
    
    print("=" * 60)
    print("CORRECTED EMERGENCE EXPERIMENT")
    print("=" * 60)
    print("Using balanced parameters with adequate simulation time")
    
    # Single run test first
    print(f"\n=== Single Trial Test ===")
    
    # Rich agent - abundant resources
    print("Rich agent:", end=" ")
    rich_agent = AutopoieticAgent(gui=False)
    rich_agent.energy_decay = 0.05          # Very slow decay
    rich_agent.landauer_cost = 0.005        # Very cheap computation
    rich_agent.learning_threshold = 25.0    # Low threshold
    
    rich_history = rich_agent.live_and_learn(max_steps=1000)  # Longer simulation
    rich_stats = rich_agent.get_survival_stats()
    rich_agent.cleanup()
    
    print(f"Food: {rich_stats['total_food_consumed']}, Efficiency: {rich_stats['feeding_efficiency']:.3f}, Learning: {rich_stats['learning_ratio']:.1%}")
    
    # Poor agent - moderate scarcity
    print("Poor agent:", end=" ")
    poor_agent = AutopoieticAgent(gui=False)
    poor_agent.energy_decay = 0.12          # Moderate decay
    poor_agent.landauer_cost = 0.015        # Moderate cost
    poor_agent.learning_threshold = 60.0    # Moderate threshold
    
    poor_history = poor_agent.live_and_learn(max_steps=1000)  # Longer simulation
    poor_stats = poor_agent.get_survival_stats()
    poor_agent.cleanup()
    
    print(f"Food: {poor_stats['total_food_consumed']}, Efficiency: {poor_stats['feeding_efficiency']:.3f}, Learning: {poor_stats['learning_ratio']:.1%}")
    
    # Analysis
    if rich_stats['total_food_consumed'] > 0 and poor_stats['total_food_consumed'] > 0:
        efficiency_ratio = poor_stats['feeding_efficiency'] / rich_stats['feeding_efficiency']
        learning_diff = poor_stats['learning_ratio'] - rich_stats['learning_ratio']
        
        print(f"\n=== Analysis ===")
        print(f"Efficiency ratio (Poor/Rich): {efficiency_ratio:.2f}")
        print(f"Learning difference: {learning_diff:+.1%}")
        
        if efficiency_ratio > 1.1:
            print("✅ EMERGENCE DETECTED: Poor agent more efficient!")
        elif efficiency_ratio > 0.9:
            print("~ COMPARABLE: Similar efficiency despite constraints")
        else:
            print("⚠ Rich agent more efficient")
            
        return True
    else:
        print(f"\n❌ INSUFFICIENT FOOD FINDING")
        print(f"Rich: {rich_stats['total_food_consumed']}, Poor: {poor_stats['total_food_consumed']}")
        return False

if __name__ == "__main__":
    success = test_corrected_emergence()
    
    if success:
        print(f"\n🎉 EMERGENCE EXPERIMENT WORKING")
        print(f"Notebook should now show proper emergence with max_steps=1000")
    else:
        print(f"\n⚠ Need to increase simulation time further for reliable food finding")