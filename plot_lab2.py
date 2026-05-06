import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

benchmarks = [
    "500.perlbench_r", "502.gcc_r", "503.bwaves_r", "505.mcf_r",
    "507.cactuBSSN_r", "508.namd_r", "510.parest_r", "511.povray_r",
    "519.lbm_r", "520.omnetpp_r", "521.wrf_r", "523.xalancbmk_r",
    "525.x264_r", "526.blender_r", "527.cam4_r", "531.deepsjeng_r",
    "538.imagick_r", "541.leela_r", "544.nab_r", "548.exchange2_r",
    "549.fotonik3d_r", "554.roms_r", "557.xz_r"
]

configs = [
    "dcache_32k_4assoc", "dcache_4k_1assoc", "dcache_4k_4assoc",
    "dcache_4k_64assoc", "dcache_256k_1assoc", "dcache_256k_4assoc",
    "dcache_256k_64assoc"
]

config_labels = ["32K/4", "4K/1", "4K/4", "4K/64", "256K/1", "256K/4", "256K/64"]
simdir = os.path.expanduser("~/exp/simulations")

def parse_stat(filepath, key):
    try:
        with open(filepath) as f:
            for line in f:
                if line.strip().startswith(key + ","):
                    parts = line.strip().split(",")
                    return float(parts[-1].strip())
    except:
        pass
    return None

# Collect data
ipc_data = {}
miss_ratio_data = {}

for bench in benchmarks:
    ipc_data[bench] = []
    miss_ratio_data[bench] = []
    for cfg in configs:
        core_csv = f"{simdir}/{bench}/lab2/{cfg}/core.stat.0.csv"
        mem_csv  = f"{simdir}/{bench}/lab2/{cfg}/memory.stat.0.csv"

        cycles = parse_stat(core_csv, "Cumulative_Cycles")
        instrs = parse_stat(core_csv, "Cumulative_Instructions")
        ipc = instrs / cycles if (cycles and instrs) else 0
        ipc_data[bench].append(ipc)

        hits   = parse_stat(mem_csv, "DCACHE_HIT_total_count")
        misses = parse_stat(mem_csv, "DCACHE_MISS_total_count")
        total  = (hits or 0) + (misses or 0)
        ratio  = misses / total if total > 0 else 0
        miss_ratio_data[bench].append(ratio)

# Add average
def add_avg(data):
    result = {}
    for k, v in data.items():
        result[k] = v
    avg = [np.mean([data[b][i] for b in benchmarks]) for i in range(len(configs))]
    result["Average"] = avg
    return result

ipc_data = add_avg(ipc_data)
miss_ratio_data = add_avg(miss_ratio_data)
all_benchmarks = benchmarks + ["Average"]

# Split into 3 groups + average in last group
groups = [
    all_benchmarks[0:8],
    all_benchmarks[8:16],
    all_benchmarks[16:23] + ["Average"]
]

colors = plt.cm.tab10.colors[:7]

def plot_grouped_bar(data, ylabel, title_prefix, filename):
    fig, axes = plt.subplots(1, 3, figsize=(26, 5))
    for gi, group in enumerate(groups):
        ax = axes[gi]
        x = np.arange(len(group))
        width = 0.11
        for ci, (cfg, label) in enumerate(zip(configs, config_labels)):
            vals = [data[b][ci] for b in group]
            ax.bar(x + ci * width, vals, width, label=label, color=colors[ci])
        ax.set_xticks(x + width * 3)
        ax.set_xticklabels([b.split(".")[1] if "." in b else b for b in group],
                           rotation=45, ha='right', fontsize=8)
        ax.set_ylabel(ylabel)
        ax.set_title(f"{title_prefix} (Part {gi+1})")
        if gi == 0:
            ax.legend(title="DCache Size/Assoc", fontsize=7, title_fontsize=7)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved {filename}")

plot_grouped_bar(ipc_data, "IPC", "IPC by DCache Config", "/home/aditya/plot_ipc.png")
plot_grouped_bar(miss_ratio_data, "Miss Ratio", "DCache Miss Ratio", "/home/aditya/plot_missratio.png")
print("Done!")
