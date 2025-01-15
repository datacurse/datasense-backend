import pandas as pd
import matplotlib.pyplot as plt


def plot_simulation_results(csv_file='simulation_results.csv'):
    data = pd.read_csv(csv_file)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Temperature (red line)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax1.plot(data['time'], data['temperature'],
             color='red', label='Temperature')
    ax1.tick_params(axis='y', labelcolor='red')

    # Power (blue dashed line)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Power (W)', color='blue')
    ax2.plot(data['time'], data['power'], 'b--', label='Power')
    ax2.tick_params(axis='y', labelcolor='blue')

    plt.title('Thermal System Simulation')
    ax1.grid()

    # Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='right')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_simulation_results()
